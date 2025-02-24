import json
import os
import pyodbc
import sqlalchemy

class DataPipeline:
    """Orchestrates the full ETL process."""
    def __init__(self, state, source, db_connection):
        self.extractor = DataClient(state)
        self.processor = DataProcessor()
        self.loader = DataClient(db_connection)

        self.source = source

    def run(self, table_name):
        raw_data = self.extractor.extract_data(self.source)
        transformed_data = self.processor.transform_data(raw_data)
        self.loader.upsert_data(table_name, transformed_data)


class DataClient:
    """
    Client for extraction and loading of data.
    """
    def __init__(self, state, db_connection):
        self.state = state
        self.db_connection = db_connection

    def read_from_raw(self, source):
        review_dir = os.path.join(self.state, source, 'reviews/')
        metadata_dir = os.path.join(self.state, source, 'metadata/')

        reviews, metadata = [], []

        for file_name in os.listdir(review_dir):
            review_file = os.path.join(review_dir, file_name)
            metadata_file = os.path.join(metadata_dir, f"meta_{os.path.basename}")

            if os.path.isfile(review_file):
                with open(review_file, 'r') as fp:
                    for line in fp:
                        reviews.append(json.loads(line.strip()))

            if os.path.isfile(metadata_file):
                with open(metadata_file, 'r') as fp:
                    for line in fp:
                        metadata.append(json.loads(line.strip()))

        return reviews, metadata
    
    def create_payload(self, processed):
        raise NotImplementedError
    
    def push_to_curated(self, curated):
        raise NotImplementedError

    
class DataProcessor:
    """
    Handles the transformation of data.
    """
    def __init__(self):
        self.secret = "placeholder"

    def data_cleaning(self, data):
        raise NotImplementedError

    def feature_engineering(self, data):
        raise NotImplementedError
    
    def transform_data(self, data):
        data = self.data_cleaning(data)
        data = self.feature_engineering(data)
        return data    