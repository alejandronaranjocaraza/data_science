'''
Healthec
Alejandro Naranjo Caraza
source: https://www.datacamp.com/tutorial/getting-started-with-apache-airflow

This script is part of DataCamp Getting Started with Airflow Article
This provides the basic DAG (Directed Accyclic Graph) template for Ariflow using the TaskFlow API.
All code is based on this source. Comments were added while reviewing the code.
'''


from airflow.decorators import dag, task
from datetime import datetime
import pandas as pd

# New DAG instance
@dag(
    start_date=datetime(year=2023, month=1, day=1, hour=9, minute=0),
    schedule="@daily",
    catchup=True,
    max_active_runs=1
)

# Notice dag-id is specified with function name
# All functions under etl function will be set as instances of python operators linked to same dag
def weather_etl():
    @task()
    # instance of python operator will point to extrct_data function with extract_data id
    def extract_data():
        # Print message, return a response
        print("Extracting data from an weather API")
        return {
            "date": "2023-01-01",
            "location": "NYC",
            "weather": {
                "temp": 33,
                "conditions": "Light snow and wind"
            }
        }

    @task()
    # instance of python operator will point to transform_data
    # task-id is assigned with function name
    def transform_data(raw_data):
        # Transform response to a list
        transformed_data = [
            [
                raw_data.get("date"),
                raw_data.get("location"),
                raw_data.get("weather").get("temp"),
                raw_data.get("weather").get("conditions")
            ]
        ]
        return transformed_data

    @task()
    # final instance of python operator simulates data loading (simply prints data
    def load_data(transformed_data):
        # Load the data to a DataFrame, set the columns
        loaded_data = pd.DataFrame(transformed_data)
        loaded_data.columns = [
            "date",
            "location",
            "weather_temp",
            "weather_conditions"
        ]
        print(loaded_data)

    # set dependencies using function calls
    raw_dataset = extract_data()
    transformed_dataset = transform_data(raw_dataset)
    load_data(transformed_dataset)


# allow the dag to run
weather_etl()
