import os
import sys
import pandas as pd
from pymongo import MongoClient

# =========================
# CONFIGURATION
# =========================

# Get project root directory (go up 3 levels from this file)
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

# Path to Spark output results (CSV files)
RESULT_DIR = os.path.join(BASE_DIR, "output", "spark_results")

# Add project root to Python module search path
# This allows importing config module correctly
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Import MongoDB configuration
from config.config import MONGO_URI, DB_NAME

# =========================
# CONNECT TO MONGODB
# =========================

print("Connecting to MongoDB...")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

print("Connected successfully")

# =========================
# HELPER FUNCTION
# =========================

def upload_csv_to_collection(file_name, collection_name):
    """
    Reads a CSV file and uploads its content to a MongoDB collection.

    Parameters:
    - file_name: name of the CSV file
    - collection_name: target MongoDB collection name
    """

    # Build full file path
    file_path = os.path.join(RESULT_DIR, file_name)

    # Check if file exists
    if not os.path.exists(file_path):
        print(f"[SKIP] {file_name} not found")
        return

    print(f"\nUploading {file_name} → {collection_name}")

    # Read CSV into pandas DataFrame
    df = pd.read_csv(file_path)

    # Convert DataFrame to list of dictionaries
    data = df.to_dict("records")

    # Get MongoDB collection
    collection = db[collection_name]

    # Clear existing data to avoid duplicates
    collection.delete_many({})

    # Insert new data
    if data:
        collection.insert_many(data)
        print(f"[OK] Inserted {len(data)} records into {collection_name}")
    else:
        print("[WARNING] No data to insert")

# =========================
# 1. SPARK ANALYSIS RESULTS
# =========================

upload_csv_to_collection("category_counts.csv", "analysis_category_counts")
upload_csv_to_collection("shift_counts.csv", "analysis_shift_counts")
upload_csv_to_collection("zone_counts.csv", "analysis_zone_counts")
upload_csv_to_collection("status_counts.csv", "analysis_status_counts")
upload_csv_to_collection("avg_rssi_by_zone.csv", "analysis_avg_rssi")
upload_csv_to_collection("active_work_by_forklift.csv", "analysis_active_work")
upload_csv_to_collection("unauthorized_by_forklift.csv", "analysis_unauthorized")
upload_csv_to_collection("spark_sql_zone_shift_summary.csv", "analysis_zone_shift")
upload_csv_to_collection("spark_sql_offline_summary.csv", "analysis_offline")

# =========================
# 2. PREDICT RESULTS
# =========================

upload_csv_to_collection("predict_downtime_by_forklift.csv", "predict_downtime")
upload_csv_to_collection("predict_offline_risk.csv", "predict_offline")
upload_csv_to_collection("predict_unauthorized_risk.csv", "predict_unauthorized")
upload_csv_to_collection("predict_composite_risk_zone_shift.csv", "predict_composite")
upload_csv_to_collection("predict_zone_risk.csv", "predict_zone")
upload_csv_to_collection("predict_shift_risk.csv", "predict_shift")

# =========================
# FINISH
# =========================

print("\nAll results written to MongoDB successfully.")