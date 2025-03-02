import os
import json

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
        self.engine = create_engine(db_connection)
        self.session = sessionmaker(bind=self.engine)

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
    
    def _read_from_lib(self, tables: list):
        for dataset in tables:
            reviews = datasets.load_dataset(
                self.web_connections, f"raw_review_{dataset}", trust_remote_code=True)["full"]
            metadata = datasets.load_dataset(
                self.web_connections, f"raw_meta_{dataset}", trust_remote_code=True)
        return reviews, metadata

    def _initialize_schema(self, schema_script_path):
        with self.engine.connect() as conn:
            with open(schema_script_path, 'r') as file:
                schema_sql = file.read()
            conn.execute(text(schema_sql))
            conn.commit()

    def _insert_items(self, items):
        """Bulk insert or update items into the database."""
        session = self.Session()
        try:
            item_data = [
                {
                    "parent_asin": item["parent_asin"], 
                    "title": item["title"], 
                    "price": item["main_category"],
                    "store": item["store"]
                }
                for item in items
            ]

            item_query = text("""
                INSERT INTO items (parent_asin, title, main_category, store)
                VALUES (:parent_asin, :title, :main_category, :store)
                ON CONFLICT (parent_asin) 
                DO UPDATE SET
                    title = EXCLUDED.title,
                    main_category = EXCLUDED.main_category,
                    store = EXCLUDED.store
                RETURNING item_id, parent_asin;
            """)
            
            inserted_items = session.execute_many(item_query, item_data)
            session.commit()

            metrics_data = [
                {
                    "item_id": row.item_id, 
                    "average_rating": item["average_rating"], 
                    "rating_number": item["rating_number"], 
                    "price": item["price"]
                }
                for row, item in zip(inserted_items, items)
            ]

            if metrics_data:
                metrics_query = text("""
                    INSERT INTO item_metrics (item_id, average_rating, rating_number, price)
                    VALUES (:item_id, :average_rating, :rating_number, :price)
                    ON CONFLICT (item_id) 
                    DO UPDATE SET 
                        average_rating = EXCLUDED.average_rating,
                        rating_number = EXCLUDED.rating_number,
                        price = EXCLUDED.price;
                """)
                session.execute_many(metrics_query, metrics_data)
                session.commit()

        except Exception as e:
            session.rollback()
            print(f"Error during bulk insert into items: {e}")
        finally:
            session.close()

    def _insert_reviews(self, reviews):
        """Bulk insert or update reviews into the database."""
        session = self.Session()
        try:
            asin_list = {review["parent_asin"] for review in reviews}  

            item_id_query = text("""
                SELECT item_id, parent_asin FROM items WHERE parent_asin = ANY(:asin_list);
            """)

            item_id_mapping = {
                row.parent_asin: row.item_id
                for row in session.execute(item_id_query, {"asin_list": list(asin_list)})
            }

            reviews_data = [
                {
                    "review_id": review["review_id"],
                    "item_id": item_id_mapping.get(review["parent_asin"]),
                    "rating": review["rating"],
                    "timestamp": review["timestamp"],
                    "helpful_vote": review["helpful_vote"],
                    "title": review["title"],
                    "text": review["text"],
                }
                for review in reviews if review["parent_asin"] in item_id_mapping
            ]

            if reviews_data:
                review_query = text("""
                    INSERT INTO reviews (review_id, item_id, rating, timestamp, helpful_vote, title, text)
                    VALUES (:review_id, :item_id, :rating, :timestamp, :helpful_vote, :title, :text)
                    ON CONFLICT (review_id)
                    DO UPDATE SET
                        rating = EXCLUDED.rating,
                        timestamp = EXCLUDED.timestamp,
                        helpful_vote = EXCLUDED.helpful_vote,
                        title = EXCLUDED.title,
                        text = EXCLUDED.text;
                """)
                session.execute_many(review_query, reviews_data)
                session.commit()

        except Exception as e:
            session.rollback()
            print(f"Error during bulk insert into reviews: {e}")
        finally:
            session.close()

    def init_database(self, mode="test"):
        raise NotImplementedError
    
    def get_items(self):
        raise NotImplementedError
    
    def get_reviews(self):
        raise NotImplementedError