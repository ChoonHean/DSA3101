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

    def review_workflow(self):
        raise NotImplementedError