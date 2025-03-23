import yaml
import os
import time

from orm.DataClient import DataClient
from modules.img_builder import save_vis

ROOT = os.getenv(__file__)
POPULATE = False

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
    reviews_query = config["sql"]["queries"]+"reviews.sql"
    reviews = client._run_script(reviews_query)
    reviews.to_csv("data/reviews.csv", index = False)

    ###############
    # Save Images #
    ###############
    save_vis(reviews)



if __name__ == "__main__":
    start_ts = time.time()
    main()
    time_elapsed = time.time() - start_ts
    print(f"Script successfully ran in {round(time_elapsed, 2)}s")