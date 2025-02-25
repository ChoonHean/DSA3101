import os
import json

import datasets
datasets.logging.set_verbosity_error()

class DataClient:
    """
    Client for extraction and loading of data.
    Parameters:
        web (string): Web library for datasets.
        root (string): Root directory of dataclient.
        db_connection (string): Connection to postgres database.
    """
    def __init__(self, web_connection:str, root: str, db_connection: str):
        self.web = web_connection
        self.root = root
        self.db_connection = db_connection

    def read_from_local(self, source:str):
        review_dir = os.path.join(self.state, source, 'reviews/')
        metadata_dir = os.path.join(self.state, source, 'metadata/')
        for file_name in os.listdir(review_dir):
            review_file = os.path.join(review_dir, file_name)
            metadata_file = os.path.join(metadata_dir, f"meta_{os.path.basename}")
            if os.path.isfile(review_file):
                with open(review_file, 'r') as fp:
                    reviews = fp
            if os.path.isfile(metadata_file):
                with open(metadata_file, 'r') as fp:
                    metadata = fp
        return reviews, metadata
    
    def read_from_lib(self, tables: list):
        for dataset in tables:
            reviews = datasets.load_dataset(
                self.web_connections, f"raw_review_{dataset}", trust_remote_code=True)["full"]
            metadata = datasets.load_dataset(
                self.web_connections, f"raw_meta_{dataset}", trust_remote_code=True)
        return reviews, metadata

    def create_payload(self, processed):
        raise NotImplementedError
    
    def push_to_curated(self, curated):
        raise NotImplementedError