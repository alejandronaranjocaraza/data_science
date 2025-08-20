from datetime import datetime, timedelta

import pandas as pd
import requests
from airflow.decorators import task
from airflow.operators.python import get_current_context
from airflow.providers.sqlite.hooks.sqlite import SqliteHook

from airflow import DAG

# Create DAG instance
with DAG(
    dag_id="polygon_extract_financial_data",  # DAG unique ID
    start_date=datetime(2025, 1, 3),  # Import start datetime (January 1st at 9:00 a.m.)
    schedule="@daily",  # Indicate daily execution
    catchup=True,  # Catch up whenever daily extraction has not been done
    max_active_runs=1,  # Only one daily run
    default_args={
        "retries": 1,  # Each task will be retried three times if it fails
        "retry_delay": timedelta(minutes=2),  # Delay between each retry
    },
) as dag:

    # Retrieve data through polygon api
    @task(execution_timeout=timedelta(seconds=10))
    def hit_polygon_api(**context):
        context = get_current_context()
        # Instantiate a list of tickers that will be pulled and looped over

        # Hit polygon REST API
        key = "oFqrkL3zTnVJ2GmKVpUiyqjN01GXhj4h"

        stock_ticker = "AAPL"
        date_str = context["ds"]
        # date_str = "2025-01-03"
        url = f"https://api.polygon.io/v1/open-close/{
            stock_ticker}/{date_str}?adjusted=true&apiKey={key}"

        response = requests.get(url, timeout=10)
        response.raise_for_status()  # raises HTTPError for 4xx/5xx responses
        # Return the raw data
        return response.json()

    @task()
    def flatten_market_data(polygon_response, **context):
        # Use a list of keys to ensure order and presence in the DataFrame
        columns = {
            "status": "closed",
            "from": context.get("ds"),
            "symbol": "-",
            "open": None,
            "high": None,
            "low": None,
            "close": None,
            "volume": None,
            "afterHours": None,
            "preMarket": None,
        }

        # Extract values from the response dictionary
        flattened_record = {col: polygon_response.get(col) for col in columns}
        flattened_record["from"] = polygon_response.get("from") or context.get(
            "ds"
        )  # Use context ds if 'from' is missing
        flattened_record["symbol"] = (
            polygon_response.get("symbol") or "AMZN"
        )  # Default to 'AMZN' if symbol is missing

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
