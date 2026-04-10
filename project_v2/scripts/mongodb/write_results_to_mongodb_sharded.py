import os
import pandas as pd
from pymongo import MongoClient

# =========================
# CONFIGURATION
# =========================

# ⚠️ IMPORTANT:
# This URI must point to mongos (router of the sharded cluster),
# NOT a standalone mongod instance
MONGO_URI = "mongodb://localhost:27017"

# Database name
DB_NAME = "forklift_db"

# Collection names
RAW_COLLECTION = "forklift_raw_data"
RESULT_COLLECTION = "forklift_analysis_results"

# Absolute path to your CSV file (you provided this)
RAW_DATA_PATH = r"E:\HAMK\Bigdata\project_v2\output\data\machine_data.csv"

# =========================
# CONNECT TO MONGODB
# =========================
print("Connecting to MongoDB (sharded cluster via mongos)...")
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
print("Connected successfully.")

# =========================
# FUNCTION TO UPLOAD CSV
# =========================
def upload_csv(file_path, collection_name):
    """
    Reads a CSV file and inserts its content into a MongoDB collection.
    """

    if not os.path.exists(file_path):
        print(f"[ERROR] File not found: {file_path}")
        return

    print(f"\nUploading {file_path} → {collection_name}")

    # Read CSV into DataFrame
    df = pd.read_csv(file_path)

    # Convert DataFrame to list of dictionaries
    data = df.to_dict("records")

    collection = db[collection_name]

    # Optional: clear existing data to avoid duplicates
    collection.delete_many({})

    if len(data) > 0:
        collection.insert_many(data)
        print(f"Inserted {len(data)} records into '{collection_name}'")
    else:
        print("No data to insert.")

# =========================
# MAIN EXECUTION
# =========================

# Upload raw dataset (this should be your sharded collection)
upload_csv(RAW_DATA_PATH, RAW_COLLECTION)

print("\nAll operations completed successfully.")