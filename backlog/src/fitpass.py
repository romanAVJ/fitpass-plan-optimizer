#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 9 17:03:21 2023

@author: ravj

Modules for fitpass optimization
"""
# %% import
import pandas as pd
import numpy as np
import pulp as plp
import geopandas as gpd

from shapely.geometry import Point
from shapely.ops import cascaded_union


# =============================================================================
# Functions
# =============================================================================
# %% functions
# transform user location to epsg:6372
def get_tuples_points(point):
    return np.asarray([(point['longitude'], point['latitude'])])

def transform_points(points, from_epsg='epsg:4326', to_epsg='epsg:6372'):
    # create a geodataframe
    gdf = gpd.GeoDataFrame(
        geometry=gpd.points_from_xy(
            x=points[:, 0],
            y=points[:, 1]
        ),
        crs=from_epsg
    )
    # transform to epsg:6372
    gdf = gdf.to_crs(to_epsg)
    # return the points
    return np.array(gdf.geometry.apply(lambda x: (x.x, x.y)).tolist()) # maybe there is a more efficient weay

def normalize(x: pd.Series):
    return (x - x.min())/(x.max() - x.min())

def distance_studio_loss(distance, sensitivity='low'):
    # distance
    def exp_dist(x, alpha=1):
        return (np.exp(alpha*x)-1)/(np.exp(alpha)-1)
    
    # sensitivity
    if sensitivity == 'low':
        return exp_dist(distance, alpha=5)
    elif sensitivity == 'medium':
        return exp_dist(distance, alpha=0.1)
    elif sensitivity == 'high':
        return exp_dist(distance, alpha=-5)
    else:
        raise ValueError('sensitivity must be low, medium or high')

def distance_preference(activity, pro, ranking):     
    return activity * pro * ranking

##### distances
def get_studios(states=['MX09', 'MX15']):
    """
    Function to get the studios from fitpass website
    """
    # read data #
    df_fitpass_r = pd.read_parquet('../data/tidy_fitpass_cdmx.parquet')
    gdf_fitpass = gpd.GeoDataFrame(
        df_fitpass_r, 
        geometry=gpd.points_from_xy(df_fitpass_r.longitude, df_fitpass_r.latitude),
        crs="EPSG:4326"
    )
    # change crs to epsg:6372
    gdf_fitpass = gdf_fitpass.to_crs("EPSG:6372")

    # wrangle data #
    # get activities in a list
    gdf_fitpass_mexico_long = (
        gdf_fitpass.copy()
        .melt(
            id_vars=['gym_id'],
            value_vars=[
                'barre', 'box', 'crossfit', 'cycling', 'dance',
                'ems', 'functional', 'gym', 'hiit', 'mma', 'pilates',
                'pool', 'running', 'sports', 'wellness', 'yoga'
                ],
            var_name='activity',
        )
        .query('value >= 1')
        # compress all the activities into a list
        .groupby('gym_id', as_index=False)['activity'].apply(list)
    )
    gdf_fitpass = gdf_fitpass.merge(gdf_fitpass_mexico_long, on='gym_id', how='left')

    # hard filters #
    # no virtual classes
    gdf_fitpass = gdf_fitpass[gdf_fitpass['virtual_class'] <= 0]
    # no activities
    gdf_fitpass = gdf_fitpass.dropna(subset=['activity'])

    # generate random ranking
    rng = np.random.RandomState(8)
    gdf_fitpass["ranking"] = 4*rng.beta(5, 2, size=gdf_fitpass.shape[0]) + 1


    # reset index
    gdf_fitpass = gdf_fitpass.reset_index(drop=True)

    # return
    return gdf_fitpass

# note: this function is not to be here
def get_payloads():
    examples = dict()

    # example 1: roman
    examples['roman'] = {
        # user info
        "name": "roman",
        # location
        "location": {
            "longitude": -99.18265186842596,
            "latitude": 19.388900864307445,
        },
        # user loss distance to studios
        "distance_sensitivity": 'medium', # low, medium, high
        # user preferences
        "preferences": {
            "love_activities": ["barre", "yoga", "cycling", "pilates", "gym"],
            "hate_activities": ["crossfit", "functional"],
        },
        # constraints
        "is_pro": 1,
        "max_allowed_classes_per_class": 4,
        "num_classes_per_month": 23,
    }
    return examples

def distances_user_studios(gdf, user_info, use_ranking=True):
    # copy
    gdf = gdf.copy()

    #### distance to studios ####
    # get user location in meters
    user_location = transform_points(get_tuples_points(user_info['location']))
    # get distance to studios
    gdf['distance'] = gdf.distance(Point(user_location[0])) / 1000 # in km's
    # filter by distance
    gdf = gdf[gdf['distance'] <= gdf['distance'].quantile(0.9)] # less than 90% of the studios
    # get distance loss
    gdf['distance_loss'] = distance_studio_loss(
        distance=normalize(gdf['distance'].copy()),
        sensitivity=user_info['distance_sensitivity']
        )

    #### user preferences ####
    # activity preference
    gdf['preference'] = np.select(
        [
            gdf['activity'].apply(
                lambda x: any([i in user_info['preferences']['love_activities'] for i in x])
                ),
            gdf['activity'].apply(
                lambda x: any([i in user_info['preferences']['hate_activities'] for i in x])
                )
        ],
        [
            3,
            -2
        ],
        default=1   
    )
    # pro preference
    # filter by pro if user is pro
    gdf = gdf[gdf['pro_status'] <= user_info['is_pro']]
    gdf['pro_preference'] = np.where(gdf['pro_status'] > 0, 3, 1) # always prefer pro's
    # ranking
    gdf['ranking_preference'] = np.where(use_ranking, gdf['ranking'], 1)
    # preference score
    gdf['preference_score'] = normalize(distance_preference(
        activity=gdf['preference'],
        pro=gdf['pro_preference'],
        ranking=gdf['ranking_preference']
    ))
    
    # reset index
    gdf = gdf.reset_index(drop=True)
    return gdf

#### optimization
# gym class
class Gym:
    def __init__(self, dict_gym, variable):
        # pulp variable for optimization
        self.pulp_var = variable

        # self vars
        self.id = dict_gym['gym_id']
        self.name = dict_gym['gym_name']
        self.point = dict_gym['geometry']
        
        # values for the optimization
        self.distance = dict_gym['distance_loss']
        self.ranking = dict_gym['preference_score']
        # values for constraints
        self.activities = dict_gym['activity']

    def __str__(self) -> str:
        # lower case name
        # TODO: better representation
        tidy_name = self.name.lower()
        s = f"{tidy_name}: {int(self.pulp_var.value())} times. (id: {self.id})"
        return s
    
    def compare_activity(self, activity):
        return activity in self.activities
    
    def get_distance(self):
        return self.distance * self.pulp_var
    
    def get_preference(self):
        return self.ranking * self.pulp_var
    
    def get_variable(self):
        return self.pulp_var
    
    def __lt__(self, other):
        return self.pulp_var.value() < other
    
    def __le__(self, other):
        return self.pulp_var.value() <= other
    
    def __ge__(self, other):
        return self.pulp_var.value() >= other
    
    def __gt__(self, other):
        return self.pulp_var.value() > other
    
    def __eq__(self, other):
        return self.pulp_var.value() == other

def create_variables(df, user_info, list_activities):
    #### gym variables (decision variables | X) ####
    gym_dict = dict()
    n_classes_dict = dict()
    activities_dict = dict()

    # create gym variables
    for i, row in df.iterrows():
        # get gym_id
        gym_id = row['gym_id']

        # gym vars
        gym_dict[gym_id] = Gym(
            dict_gym=row,
            variable=plp.LpVariable(
                name=f"gym{gym_id}",
                lowBound=0,
                upBound=np.min([user_info["max_allowed_classes_per_class"], 4]),
                cat='Integer'
            ))
        
        # class vars
        n_classes_dict[gym_id] = plp.LpVariable(
            name=f"class{gym_id}",
            lowBound=0, upBound=1, cat='Binary'
        )    
        
    #### support variables ####
    # create a list of auxiliar variables
    for activity in list_activities:
        # pulp variable
        activities_dict[activity] = plp.LpVariable(
            name=f"activity_{activity}",
            lowBound=0, upBound=1, cat='Binary'
        )

    return {'gym': gym_dict, 'class': n_classes_dict, 'activity': activities_dict}

def create_problem(df, user_info, list_activities, dict_weights):
    #### create variables ####
    # get optimization vars
    dict_variables = create_variables(df, user_info, list_activities)
    # unpack variables (WIP: GET THIS VARIABLES)
    gym_dict = dict_variables['gym']
    n_classes_dict = dict_variables['class']
    activities_dict = dict_variables['activity']

    #### create problem ####
    # init
    prob = plp.LpProblem("Fitpass", plp.LpMinimize)
    # get distance
    f_distance = plp.lpSum([gym.get_distance() for gym in gym_dict.values()])
    f_preference = plp.lpSum([gym.get_preference() for gym in gym_dict.values()])
    f_activity = plp.lpSum((activities_dict.values()))
    f_n_classes = plp.lpSum(list(n_classes_dict.values()))
    # generate objective function
    prob += (
        dict_weights['distance'] * f_distance
        - dict_weights['preference'] * f_preference 
        - dict_weights['activity'] * f_activity 
        - dict_weights['class'] * f_n_classes,
        "objective function"
    )

    #### constraints ####
    # constraint of max classes per month
    prob += (
        plp.lpSum([gym.get_variable() for gym in gym_dict.values()]) == user_info['num_classes_per_month'],
        "classes per month"
    )

    # auxiliar variable constraint for activities
    for k, v in activities_dict.items():
        # get all the gyms with the activity
        gyms_with_activity = [gym for gym in gym_dict.values() if gym.compare_activity(k)]
        # add constraint
        prob += (
            v <= plp.lpSum([gym.get_variable() for gym in gyms_with_activity]),
            f"activity_{k}"
        )

    # auxiliar variable constraint for number of classes in the same gym
    for k, v in n_classes_dict.items():
        # get all the gyms with the activity
        gym = gym_dict[k]
        # add constraint
        prob += (
            v <= gym.get_variable(),
            f"classes_at_gym{k}"
        )

    return {'problem': prob, 'variables': dict_variables}

def solve_problem(prob, dict_variables):
    # solve the problem
    prob.solve(plp.PULP_CBC_CMD(msg=0))

    # look if the problem was solved
    if plp.LpStatus[prob.status] == 'Optimal':
        # get the solution
        solution = [gym for gym in dict_variables['gym'].values() if gym > 0]
        # get activities done
        activities_with_classes = [
            activity for activity in dict_variables['activity'].values() 
                if activity.value() > 0
            ]
    
    # look for constrain
    else:
        print("The problem has no solution")
        solution = None
        activities_with_classes = None
    return {'solution': solution, 'activities': activities_with_classes}

def generate_solution(df, solutions):
    # get gym id's
    gym_ids = [getattr(gym, "id") for gym in solutions]
    gym_times = [int(gym.get_variable().value()) for gym in solutions]

    df_gyms = pd.DataFrame({
        'gym_id': gym_ids,
        'gym_times': gym_times
    })

    # filter df
    df_solution = (
        df.copy()
        [['gym_id', 'gym_name', 'activity', 'distance', 'preference_score', 
          'geometry', 'pro_status']]
        .merge(df_gyms, on='gym_id', how='inner')
        .sort_values(by='gym_name', ascending=True, ignore_index=True)
        .drop(columns=['gym_id'])
        [['gym_name', 'gym_times', 'activity', 'distance', 'preference_score', 
          'pro_status', 'geometry']]
    )
    return df_solution

# the app.py function
def fitpass_optimization(user_info, dict_weights):
    # load data
    df_studios = get_studios()

    # distances
    df_distances = distances_user_studios(df_studios, user_info, use_ranking=False)

    # optimization #
    # activities
    list_activities = df_distances['activity'].explode().unique().tolist()
    list_activities.sort()

    # create problem
    dict_problem = create_problem(
        df_distances, user_info, list_activities, dict_weights=dict_weights
        )

    # solve problem
    dict_solution = solve_problem(dict_problem['problem'], dict_problem['variables'])

    # get solutions #
    df_solution = generate_solution(df_distances, dict_solution['solution'])
    return df_solution

# =============================================================================
# Main
# =============================================================================
# Check if the script is run directly
if __name__ == "__main__":
    # Additional code to run when the script is executed directly
    # This block won't be executed when the script is imported as a module
    print("Running fitpass.py directly")

    # PARAMETERS
    WEIGHTS = {
        'distance': 0.6,
        'preference': 0.3,
        'activity': 0.075,
        'class': 0.025
    }

    payload = get_payloads()['roman']

    df_solutions = fitpass_optimization(payload, WEIGHTS)
    print(df_solutions)