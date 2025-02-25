import pandas as pd
from typing import Iterable

class DataProcessor:
    """
    Handles the transformation of data.
    """
    def __init__(self):
        pass

    def review_cleaning(self, review:dict):
        raise NotImplementedError

    def review_engineering(self, review: dict):
        raise NotImplementedError

    def review_workflow(self, reviews: Iterable[dict]):
        for review in reviews:
            reviews = self.review_cleaning(review)
            reviews = self.review_engineering(review)
        raise NotImplementedError

    def meta_cleaning(self, metadata: dict):
        raise NotImplementedError

    def meta_engineering(self, metadata: dict):
        raise NotImplementedError

    def meta_workflow(self, metadata: Iterable[dict]):
        for meta in metadata:
            meta = self.meta_cleaning(meta)
            meta = self.meta_engineering(meta)
        return meta

    def transform_data(self, data:tuple):
        reviews, metadata = data
        reviews, metadata = self.review_workflow(reviews), self.meta_workflow(metadata)
        return reviews, metadata