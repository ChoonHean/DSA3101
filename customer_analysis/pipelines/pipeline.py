from pipeline_utils.DataClient import DataClient
from pipeline_utils.DataProcessor import DataProcessor

class DataPipeline:
    """
    Orchestrates the full ETL process.
    Parameters:
        state (string): Root directory of instantiation.
        source (string): Path to source folder containing raw data.
        db_connection (string): Connection to postgresql db.
    """
    def __init__(self, web_connection, root, source, db_connection):
        self.client = DataClient(web_connection, root, db_connection)
        self.processor = DataProcessor()
        self.source = source

    def run_pipeline(self, tables=None):
        if tables:
            raw_data = self.client.read_from_lib(tables)
        else:
            raw_data = self.client.read_from_local(self.source)
        transformed_data = self.processor.transform_data(raw_data)
        self.client.upsert_data(transformed_data)
