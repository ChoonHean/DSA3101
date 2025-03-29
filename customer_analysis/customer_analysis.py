import yaml
import os
import time

from orm.DataClient import DataClient
from modules.img_builder import _clean, word_cloud, agg_reviews

ROOT = os.getenv(__file__)
POPULATE = True

def main():
    #####################
    # DB Initialization #
    #####################
    with open("config/client.yaml", "r") as file:
        config = yaml.safe_load(file)
    client = DataClient(
        web_connection=config["paths"]["web"],
        root=ROOT,
        db_connection=config["paths"]["connection"]
    )
    kwargs = {
        "mode": "web",
        "category": "Amazon_Fashion"
    }
    if POPULATE:
        client.populate_database(config["sql"]["db"], kwargs)

    #################
    # Execute query #
    #################
    DATA_DIR = config["path"]["data"]
    reviews_query = config["sql"]["queries"]+"reviews.sql"
    reviews = client._run_script(reviews_query)
    reviews.to_csv(f"{DATA_DIR}reviews.csv", index = False)
    print(f"Saved raw data to {DATA_DIR}")
    categorized = _clean(reviews)
    categorized.to_csv(f"{DATA_DIR}categorized.csv", index = False)
    print(f"Saved processed file to {DATA_DIR}")

    ###############
    # Save Images #
    ###############
    EXPORT_DIR = config["path"]["exports"]
    agg_reviews(categorized, EXPORT_DIR)
    word_cloud(categorized, 4, EXPORT_DIR, "right", "price_value")
    word_cloud(categorized, 2, EXPORT_DIR, "left", "price_value")
    word_cloud(categorized, 4, EXPORT_DIR, "right")
    word_cloud(categorized, 2, EXPORT_DIR, "left")
    print(f"Saved visualisations to {EXPORT_DIR}")

if __name__ == "__main__":
    start_ts = time.time()
    main()
    time_elapsed = time.time() - start_ts
    print(f"Script successfully ran in {round(time_elapsed, 2)}s")