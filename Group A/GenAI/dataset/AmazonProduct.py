from datasets import load_dataset
import pandas as pd
import numpy as np


def dataset_to_dataframe(dataset):
    """
    Convert any hugging face dataset into a pandas DataFrame
    :param dataset: Any hugging face dataset of the class 'datasets.arrow_dataset.Dataset'
    :return: pandas DataFrame
    """
    return pd.DataFrame({column:dataset[column] for column in dataset.column_names})

# Load in the dataset using HuggingFace
dataset = load_dataset("McAuley-Lab/Amazon-Reviews-2023", "raw_review_Amazon_Fashion", trust_remote_code=True)["full"]
metadata = load_dataset("McAuley-Lab/Amazon-Reviews-2023", "raw_meta_Amazon_Fashion", trust_remote_code=True)["full"]
fashion_review = dataset_to_dataframe(dataset)
print(fashion_review[fashion_review["parent_asin"] != fashion_review["asin"]])
#There are 61188 rows of review contain different parent_asin from asin, the documentation says just use the parent_asin
fashion_review.drop("asin", inplace = True, axis = 1)
fashion_meta = dataset_to_dataframe(metadata)
fashion_meta.rename(columns = {"title": "name"}, inplace = True)

# Merge the user review data with extra information on the items metadata
fashion_df = pd.merge(fashion_review, fashion_meta, how ="left", on ="parent_asin", suffixes = ["_review", "_meta"])

# Storing the fashion user review and fashion product to the dataset
fashion_df.to_parquet("dataset/fashion_df.gzip")
fashion_meta.to_parquet("dataset/fashion_meta.gzip")

# Try reading the parquet object to ensure it's readable
a = pd.read_parquet("dataset/fashion_df.gzip")