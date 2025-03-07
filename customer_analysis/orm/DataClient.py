import os
import pandas as pd
import datetime
import datasets

datasets.logging.set_verbosity_error()

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text

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
        self.engine = create_engine(db_connection, echo=True)
        self.Session = sessionmaker(bind=self.engine)

    def _read_from_local(self, source:str):
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
    
    def _read_from_lib(self, dataset: str):
        reviews = datasets.load_dataset(
            self.web, f"raw_review_{dataset}", trust_remote_code=True)["full"]
        metadata = datasets.load_dataset(
            self.web, f"raw_meta_{dataset}", trust_remote_code=True)["full"]
        return reviews, metadata

    def _initialize_schema(self, schema_script_path):
        with self.engine.connect() as conn:
            with open(schema_script_path, 'r') as file:
                schema_sql = file.read()
            conn.execute(text(schema_sql))
            conn.commit()
        print("Tables created.")

    def _insert_items(self, items):
        """Bulk insert or update items into the database."""
        with self.engine.connect() as conn:
            columns = ["parent_asin", "title", "main_category", "store", "average_rating", "rating_number", "price"]
            item_data = [
                {
                    x: item[x] for x in columns
                }
                for item in items if item["price"]!="None"
            ]
            try:
                item_query = text("""
                    INSERT INTO items (parent_asin, title, main_category, store, average_rating, rating_number, price)
                    VALUES (:parent_asin, :title, :main_category, :store, :average_rating, :rating_number, :price)
                    ON CONFLICT (parent_asin) 
                    DO UPDATE SET
                        title = EXCLUDED.title,
                        main_category = EXCLUDED.main_category,
                        store = EXCLUDED.store,
                        average_rating = EXCLUDED.average_rating,
                        rating_number = EXCLUDED.rating_number,
                        price = EXCLUDED.price;
                """)
                conn.execute(item_query, item_data)
                conn.commit() 

            except Exception as e:
                conn.rollback()
                print(f"Error inserting items: {e}")  

            conn.close()
            

    def _insert_reviews(self, reviews):
        """Bulk insert or update reviews into the database."""
        columns = ["parent_asin", "rating", "timestamp", "helpful_vote", "verified_purchase", "title", "text"]
        review_data = [
            {
                x: review[x] if x != "timestamp" else datetime.datetime.fromtimestamp(int(review[x])/1000.0, datetime.UTC) for x in columns
            } 
            for review in reviews
        ]
        with self.engine.connect() as conn:
            try:
                review_query = text("""
                    INSERT INTO reviews (parent_asin, rating, timestamp, helpful_vote, verified_purchase, title, text)
                    VALUES (:parent_asin, :rating, :timestamp, :helpful_vote, :verified_purchase, :title, :text);
                """)
                conn.execute(review_query, review_data)
                conn.commit() 

            except Exception as e:
                conn.rollback()
                print(f"Error inserting reviews: {e}")  

            conn.close()


    def populate_database(self, script_path, kwargs):
        self._initialize_schema(script_path)
        if kwargs["mode"] == "web":
            reviews, items = self._read_from_lib(kwargs["category"])
        else:
            reviews, items = self._read_from_local(kwargs["file_path"])
        self._insert_items(items)
        self._insert_reviews(reviews)
        print("Tables created and populated!")
    
    def query_to_dataframe(self, query, params=None):
        """Run a query and return a Pandas DataFrame."""
        with self.engine.connect() as conn:
            result = conn.execute(text(query), params or {})
            return pd.DataFrame(result.fetchall(), columns=result.keys())
