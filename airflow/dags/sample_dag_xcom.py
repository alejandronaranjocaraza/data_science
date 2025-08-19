'''
Healthec
Alejandro Naranjo Caraza
source: https://www.datacamp.com/tutorial/getting-started-with-apache-airflow

This script is part of DataCamp Getting Started with Airflow Article.
This provides the basic DAG (Directed Acyclic Graph) template using XComs feature to retieve data from each task.
All code is based on this source. Comments were added while reviewing the code.
'''


import pandas as pd
from airflow import DAG
from datetime import datetime
from airflow.operators.python import PythonOperator


# New DAG instance
with DAG(
    dag_id="weather_etl",# set ID associated to dag
    start_date=datetime(year=2024, month=1, day=1, hour=9, minute=0),# set start date
    schedule="@daily",# dag will be run daily
    catchup=True,# dag will be run for every day from start date to current date
    max_active_runs=1,# ensures dag is only run once every day
    render_template_as_native_obj=True# Enables Jinja templates to be rendered as native python objects
) as dag:
    
    def extract_data_callable():
        # print message, return a response
        print("Extracting data from an weather API")
        # return python dictionary with wather information (sample database)
        return {
            "date": "2023-01-01",
            "location": "NYC",
            "weather": {
                "temp": 33,
                "conditions": "Light snow and wind"
            }
        }

    # instance of python operator created
    extract_data = PythonOperator(
        dag=dag,# operator will be part of dag we defined earier
        task_id="extract_data",# assigne a unique id to the task
        python_callable=extract_data_callable# assign python function that will be executed with this operator
    )

    def transform_data_callable(raw_data):
        # transforms return to list
        transformed_data = [
            [
                raw_data.get("date"),
                raw_data.get("location"),
                raw_data.get("weather").get("temp"),
                raw_data.get("weather").get("conditions")
            ]
        ]
        return transformed_data

    # instance of python operator created
    transform_data = PythonOperator(
        dag=dag,# operator will be part of dag we previously created
        task_id="transform_data",# assign unique id to task
        python_callable=transform_data_callable,# assign python function that will be executed
        op_kwargs={"raw_data": "{{ ti.xcom_pull(task_ids='extract_data') }}"}# dict of keyword arguments
    )

    def load_data_callable(transformed_data):
        # load the data to a DataFrame, set the columns
        loaded_data = pd.DataFrame(transformed_data)
        loaded_data.columns = [
            "date",
            "location",
            "weather_temp",
            "weather_conditions"
        ]
        print(loaded_data)# view loaded data

    # instance of python operator created
    load_data = PythonOperator(
        dag=dag,# operator will be part of our previous dag
        task_id="load_data",# same task id
        python_callable=load_data_callable,# referenced python function
        op_kwargs={"transformed_data": "{{ ti.xcom_pull(task_ids='transform_data') }}"}# key,value pairs that will be passed into load_data_callable
    )

    # sets task dependencies and sequence
    extract_data >> transform_data >> load_data
