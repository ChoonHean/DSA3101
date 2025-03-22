import yaml
import os
import time

from orm.DataClient import DataClient
# from modules.md_builder import generate_md_report
# from modules.img_builder import plt_save

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
    df = client._run_script(reviews_query)
    df.to_csv("exports/reviews.csv", index = False)

    items_query = config["sql"]["queries"]+"items.sql"
    df = client._run_script(items_query)
    df.to_csv("exports/items.csv", index = False)

    # #########################
    # # Build a markdown file #
    # #########################
    # generate_md_report()



if __name__ == "__main__":
    start_ts = time.time()
    main()
    time_elapsed = time.time() - start_ts
    print(f"Script successfully ran in {round(time_elapsed, 2)}s")