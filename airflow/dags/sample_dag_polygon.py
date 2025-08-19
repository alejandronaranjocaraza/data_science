from datetime import datetime, timedelta

import pandas as pd
import requests
from airflow.decorators import task
from airflow.providers.sqlite.hooks.sqlite import SqliteHook

from airflow import DAG

# Create DAG instance
with DAG(
    dag_id="market_etl",  # DAG unique ID
    start_date=datetime(
        2024, 1, 1, 9
    ),  # Import start datetime (January 1st at 9:00 a.m.)
    schedule="@daily",  # Indicate daily execution
    catchup=True,  # Catch up whenever daily extraction has not been done
    max_active_runs=1,  # Only one daily run
    default_args={
        "retries": 3,  # Each task will be retried three times if it fails
        "retry_delay": timedelta(minutes=5),  # Delay between each retry
    },
) as dag:

    # Retrieve data through polygon api
    @task()
    def hit_polygon_api(**context):
        # Instantiate a list of tickers that will be pulled and looped over
        stock_ticker = "AMZN"
        # Set variables
        polygon_api_key = "oFqrkL3zTnVJ2GmKVpUiyqjN01GXhj4h"

        ds = context.get(
            "ds"
        )  # Pulling ds from context will give us give us date of the data_interval_end
        # Create the URL
        url = f"https://api.polygon.io/v1/open-close/{stock_ticker}/{ds}?adjusted=true&apiKey={polygon_api_key}"
        response = requests.get(url)
        print(response)  # Fixed the typo here
        response.raise_for_status() # Add a line to raise an error for bad responses (4xx or 5xx)
        # Return the raw data
        return response.json()

    @task()
    def flatten_market_data(polygon_response, **context):
        # Use a list of keys to ensure order and presence in the DataFrame
        columns = [
            "status",
            "from",
            "symbol",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ]

        # Extract values from the response dictionary
        flattened_record = {col: polygon_response.get(col) for col in columns}
        flattened_record["from"] = polygon_response.get("from") or context.get("ds") # Use context ds if 'from' is missing
        flattened_record["symbol"] = polygon_response.get("symbol") or "AMZN" # Default to 'AMZN' if symbol is missing
        
        # Convert to a pandas DataFrame
        flattened_dataframe = pd.DataFrame([flattened_record], columns=columns)
        return flattened_dataframe

    @task()
    def load_market_data(flattened_data_frame):
        # The connection ID should match what you set in Airflow's UI
        market_database_hook = SqliteHook("market_database_conn")
        market_database_conn = market_database_hook.get_sqlalchemy_engine()
        
        # Load table to SQL database, append if it exists
        flattened_data_frame.to_sql(
            name="market_data",
            con=market_database_conn,
            if_exists="append",
            index=False,
        )

    # TaskFlow dependencies
    raw_market_data = hit_polygon_api()
    flattened_market_data = flatten_market_data(raw_market_data)
    load_market_data(flattened_market_data)
