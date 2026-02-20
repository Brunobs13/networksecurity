import os
import sys

import certifi
import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")


class NetworkDataExtract:
    def __init__(self):
        try:
            if not MONGODB_URI:
                raise ValueError("MONGODB_URI is not set in environment variables.")
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def csv_to_json_converter(self, file_path: str):
        try:
            dataframe = pd.read_csv(file_path)
            dataframe.reset_index(drop=True, inplace=True)
            records = dataframe.to_dict(orient="records")
            logging.info("Converted CSV into JSON records successfully.")
            return records
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def insert_data_mongodb(self, records, database: str, collection: str) -> int:
        try:
            client = MongoClient(MONGODB_URI, tlsCAFile=certifi.where())
            db = client[database]
            coll = db[collection]
            result = coll.insert_many(records)
            inserted_count = len(result.inserted_ids)
            logging.info("Inserted %s records into MongoDB.", inserted_count)
            return inserted_count
        except Exception as e:
            raise NetworkSecurityException(e, sys)


if __name__ == "__main__":
    try:
        file_candidates = [
            "network_data/phishingData.csv",
            "Network_Data/phisingData.csv",
        ]
        file_path = next((path for path in file_candidates if os.path.exists(path)), None)
        if not file_path:
            raise FileNotFoundError(
                "CSV file not found. Expected one of: network_data/phishingData.csv or Network_Data/phisingData.csv"
            )

        database_name = "test"
        collection_name = "network_data"

        extractor = NetworkDataExtract()
        records = extractor.csv_to_json_converter(file_path=file_path)
        inserted_records = extractor.insert_data_mongodb(
            records=records, database=database_name, collection=collection_name
        )

        print(f"Number of records inserted: {inserted_records}")
        print("Data insertion completed successfully.")
    except Exception as e:
        raise NetworkSecurityException(e, sys)
        


