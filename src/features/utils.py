'''Script containing helper functions'''
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import urllib.request
import os
import logging


def setup_logging(log_level=logging.INFO, log_format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s'):
    '''Setup logging configuration'''
    logging.basicConfig(level=log_level, format=log_format)

    # Create a directory for logs if it doesn't exist
    log_dir = os.path.join(os.path.dirname(__file__), '../logs')
    os.makedirs(log_dir, exist_ok=True)

    # Add a file handler to the root logger
    file_handler = logging.FileHandler(os.path.join(log_dir, 'app.log'))
    file_handler.setFormatter(logging.Formatter(log_format, datefmt='%Y-%m-%d %H:%M:%S'))
    logging.getLogger().addHandler(file_handler)


def add_cyclical_features(self, column_name, max_value):
    '''Add sine and cosine features for a cyclical column'''
    self.merged_data[f'{column_name}_sin'] = np.sin(2 * np.pi * self.merged_data[column_name]/max_value)
    self.merged_data[f'{column_name}_cos'] = np.cos(2 * np.pi * self.merged_data[column_name]/max_value)
    logging.info(f'Added cyclical features for {column_name}')


class Database:
    '''Class to handle database operations'''
    def __init__(self, db_dir, db_name):
        self.db_dir = db_dir
        logging.info(f"Initializing database in directory: {db_dir} with database name: {db_name}")
        os.makedirs(self.db_dir, exist_ok=True)
        self.db_path = os.path.join(self.db_dir, db_name)
        
        try:
            url_template = 'https://techassessment.blob.core.windows.net/aiap18-assessment-data/{db_name}'
            urllib.request.urlretrieve(url_template.format(db_name=db_name), self.db_path)
            self.engine = create_engine('sqlite:///' + self.db_path)
            logging.info("Database engine created successfully.")
        except Exception as e:
            logging.error(f"Failed to create database engine: {e}")
            raise SystemExit

    def query_to_dataframe(self, query):
        '''Query data from the database and return as a DataFrame'''
        logging.info(f"Executing query: {query}")
        try:
            df = pd.read_sql_query(query, self.engine)
            logging.info("Query executed successfully.")
            logging.info(f"Data queried has {df.shape[0]} rows and {df.shape[1]} columns.")
            return df
        except Exception as e:
            logging.error(f"Failed to execute query: {e}")
            raise

    def close(self):
        logging.info("Closing database connection.")
        self.engine.dispose()


def query_data_from_database(query, db_path, db_name):
    '''Orchestrates the process of querying data from the database and returning it as a DataFrame'''
    logging.info(f"Querying data from database: {db_name} at path: {db_path}")
    db = Database(db_path, db_name)

    try:
        data = db.query_to_dataframe(query)
        logging.info("Data queried successfully.")
    except Exception as e:
        logging.error(f"Failed to query data: {e}")
        raise SystemExit

    db.close()

    return data