#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 18 20:00:29 2023

@author: ravj

Script to webscrap fitpass studios and tide data
"""
# %% libraries
import pandas as pd
import numpy as np
import geopandas as gpd
import requests
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
from tqdm import tqdm 

# %% params
URL = "https://www.fitpass.com/mx/mapa"
STATES = ['MX09', 'MX15']

#### functions
## utils
def get_number_string_pair(x):
    if x is None:
        return None
    else:
        # get the first number-string pair
        number_string_pair = re.findall(r'(\d+)\s*(\w+)', x)
        if len(number_string_pair) > 0:
            return number_string_pair
        else:
            return []

def get_minutes(list_of_tuples: list[tuple]):
    # case where there are not matches
    if len(list_of_tuples) == 0:
        return np.nan
    
    # case where there are matches
    list_of_minutes = list()
    for i in list_of_tuples:
        # get rid of special spanish characters
        if i[1].replace('á', 'a').replace('ó', 'o').replace('ú', 'u').replace('í', 'i') in ['min', 'minutos', 'minutes']:
            list_of_minutes.append(i[0])

    # case where there are not matches
    if len(list_of_minutes) == 0:
        return np.nan
    else:
        return max(list_of_minutes)

## scrape
def scrape_fitpass_gyms(url: str) -> pd.DataFrame:
    """
    Scrapes gym information from the Fitpass website and returns it as a DataFrame.
    
    Args:
        url (str): The URL of the Fitpass map page to scrape.
    
    Returns:
        pd.DataFrame: A DataFrame containing gym information.
    """
    # Create a new instance of the Firefox driver
    driver = webdriver.Firefox()

    # Open the URL in the browser
    driver.get(url)

    # Wait for some time to let the dynamic content load
    driver.implicitly_wait(10)

    # Initialize an empty dictionary to store data
    gym_data = {
        'gym_name': [],
        'latitude': [],
        'longitude': [],
        'pro_status': [],
        'notes': [],
        'address': [],
        'virtual_status': [],
        'gym_id': [],
        'activities': []
    }

    try:
        # Find the <div> with class "list-group list-group-flush"
        list_group_div = driver.find_element(By.CLASS_NAME, "list-group.list-group-flush")
        
        if list_group_div:
            # Get the inner HTML content of the list group div
            list_group_html = list_group_div.get_attribute("innerHTML")
            
            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(list_group_html, 'html.parser')
            
            # Find all <div> elements with class "list-group-item py-3 text-start"
            list_group_items = soup.find_all("div", class_="list-group-item py-3 text-start")
            
            if list_group_items:
                # Use tqdm to track the progress
                for item in tqdm(list_group_items, desc="Scraping Gym Data"):
                    # Access and save the desired data attributes
                    gym_data['gym_name'].append(item["data-gym-name"])
                    gym_data['latitude'].append(item["data-gym-latitude"])
                    gym_data['longitude'].append(item["data-gym-longitude"])
                    gym_data['pro_status'].append(item["data-gym-pro"])
                    gym_data['notes'].append(item["data-gym-notes"])
                    gym_data['address'].append(item["data-gym-address"])
                    gym_data['virtual_status'].append(item["data-gym-virtual"])
                    gym_data['gym_id'].append(item["data-gym-id"])
                    
                    # Find the <span> within <div class="text-muted">
                    text_muted_div = item.find("div", class_="text-muted")
                    text_uppercase_span = text_muted_div.find("span", class_="text-uppercase")
                    gym_data['activities'].append(text_uppercase_span.get_text(strip=True))
                    
            else:
                print("No list group items found within the list group div")
        else:
            print("No list group div found")
    finally:
        # Close the browser window when done
        driver.quit()

    # Create a DataFrame from the extracted dictionary
    df = pd.DataFrame(gym_data)

    return df

def wrangle_data(df: pd.DataFrame) -> pd.DataFrame:
    # nlp to extract activities
    df['activities'] = df['activities'].str.lower()

    # second, unnest the text in 'activities' column by comma into new columns
    df_long = (
        df[['gym_id', 'activities']].copy()
        .assign(
            activities=lambda dfx: dfx['activities'].str.split(',')
        ).explode('activities'))
    
    # third, long to wide
    df_wide = (
        df_long
        .copy()
        .assign(
            activities = lambda x: 
                (x['activities'].str.strip()
                .str.replace(' ', '_')
                .str.lower()
                .str.replace(r'_\([^)]*\)', '', regex = True) # get rid from "_()" in "prefix_()"
                ),
            activities_present = 1
        )
        .replace({
            'albercas': 'pool',
            'artes_marciales': 'mma',
            'baile': 'dance',
            'barre': 'barre',
            'box': 'box',
            'clase_virtual': 'virtual_class',
            'crossfit': 'crossfit',
            'cycling': 'cycling',
            'deportes': 'sports',
            'ems': 'ems',
            'funcional': 'functional',
            'gym': 'gym',
            'hiit': 'hiit',
            'pilates': 'pilates',
            'running': 'running',
            'wellness': 'wellness',
            'yoga': 'yoga'
        })
        .drop_duplicates()
        .query('activities != ""')
        .pivot_table(
            index = 'gym_id',
            columns = 'activities',
            values = 'activities_present',
            fill_value = 0
        )
        .reset_index()
    )

    # fouth, get minutes
    df['possible_minutes'] = df['notes'].apply(get_number_string_pair)
    df['num_matching'] = df['possible_minutes'].apply(len) 
    df['class_minutes'] = df['possible_minutes'].apply(get_minutes)

    # fifth, merge
    df_main = (
        df
        .assign(
            pro_status = lambda x: x['pro_status'].apply(lambda x: 1 if x == 'true' else 0),
            virtual_status = lambda x: x['virtual_status'].apply(lambda x: 1 if x == 'true' else 0)
        )
        [[
            'gym_id', 'gym_name', 'pro_status', 'virtual_status',
            'class_minutes', 'notes', 
            'latitude', 'longitude', 'address'
            ]]
        .merge(
            df_wide,
            how="left",
            on='gym_id'
        )
    )
    return df_main

def filter_data(df: pd.DataFrame, states='MX09') -> pd.DataFrame:
    # df 2 gdf
    gdf = gpd.GeoDataFrame(
        df, 
        geometry=gpd.points_from_xy(df.longitude, df.latitude),
        crs="EPSG:4326"
    )

    # read states
    gdf_states = gpd.read_file('../data/mexico_states')

    # filter by state
    polygon_mex = gdf_states[gdf_states['CODIGO'].isin(states)].unary_union
    gdf = gdf[gdf.within(polygon_mex)]

    # drop geometry
    gdf = gdf.drop(columns=['geometry'])


    return pd.DataFrame(gdf.reset_index(drop=True))
#### main
# %% webscrap fitpass gyms
df_fitpass_raw = scrape_fitpass_gyms(URL)

# %% wrangle data
df_fitpass = wrangle_data(df_fitpass_raw)

# %%filter data
df_fitpass_states = filter_data(df_fitpass, states=STATES)
# %% save 2 parquet
df_fitpass_states.to_parquet('../data/tidy_fitpass_cdmx.parquet')