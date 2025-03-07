import yaml
import os
import time

from orm.DataClient import DataClient
# from modules.md_builder import generate_md_report
# from modules.img_builder import plt_save

ROOT = os.getenv(__file__)

def main():
    #####################
    # DB Initialization #
    #####################
    with open("config/client_config.yaml", "r") as file:
        config = yaml.safe_load(file)
    client = DataClient(
        web_connection=config["paths"]["web"],
        root=ROOT,
        db_connection=config["paths"]["connection"]
    )
    kwargs = {
        "mode": "web",
        "category": "All_Beauty"
    }
    client.populate_database(config["sql"]["db"], kwargs)

    #################
    # Execute query #
    #################
    # queries = config["sql"]["queries"]
    # for query in queries:
    #     df = client.query_to_dataframe(query)
    #     plt_save(df)

    # #########################
    # # Build a markdown file #
    # #########################
    # generate_md_report()



if __name__ == "__main__":
    start_ts = time.time()
    main()
    time_elapsed = time.time() - start_ts
    print(f"Script successfully ran in {round(time_elapsed, 2)}s")