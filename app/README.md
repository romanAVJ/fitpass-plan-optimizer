Fitpass Class Optimization Flask App

This Flask app provides a REST API endpoint for optimizing Fitpass class schedules. The app takes a JSON payload containing user preferences and Fitpass class data, and returns a JSON payload with the optimized class schedule.
Prerequisites
To run the app, you will need to have Python 3.x installed, along with the Flask, json, and requests libraries.
Running the App
Clone the repository to your local machine.
Open a terminal window and navigate to the directory containing the code.
Install the required dependencies:
Bash
pip install -r requirements.txt


Run the app:
Bash
FLASK_ENV=development flask run


The app will start up and listen on port 8080.

Usage
To use the app, make a POST request to the /predict endpoint with a JSON payload containing the following fields:
location: A dictionary containing the user's latitude and longitude
distance_sensitivity: The user's distance sensitivity (low, medium, or high)
preferences: A dictionary containing the user's love and hate activities
is_pro: Whether or not the user is a Fitpass Pro member
max_allowed_classes_per_class: The maximum number of classes the user is allowed to take from each studio
num_classes_per_month: The number of classes the user wants to take per month
The app will return a JSON payload with the optimized class schedule.
Example Usage
Bash
curl -X POST http://localhost:8080/predict -H "Content-Type: application/json" -d '{
  "location": {
    "latitude": 37.783333,
    "longitude": -122.416667
  },
  "distance_sensitivity": "medium",
  "preferences": {
    "love_activities": ["yoga", "dance"],
    "hate_activities": ["barre", "boxing"]
  },
  "is_pro": true,
  "max_allowed_classes_per_class": 3,
  "num_classes_per_month": 10
}'


This request will return a JSON payload with the optimized class schedule for the user.
Deployment
To deploy the app to a production environment, you can use a web server such as Gunicorn or uWSGI. You will also need to set the FLASK_ENV environment variable to production.
