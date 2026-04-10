import os
import sys
import time
import pandas as pd
from pymongo import MongoClient

# ----------------------------
# Make project root importable
# ----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from config.config import MONGO_URI, DB_NAME, COLLECTION_NAME

# ----------------------------
# 1. Connect to MongoDB
# ----------------------------
print("Connecting to MongoDB...")
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]
print("Connected successfully")

# ----------------------------
# 2. Load dataset
# ----------------------------
print("Loading dataset...")
file_path = os.path.join(BASE_DIR, "data", "forklift_dataset.csv")
df = pd.read_csv(file_path)
print(f"Dataset loaded: {df.shape[0]} rows")

# ----------------------------
# 3. Convert to MongoDB format
# ----------------------------
data = df.to_dict(orient="records")

# ----------------------------
# 4. Clear old data
# ----------------------------
print("Clearing old data...")
collection.delete_many({})

# ----------------------------
# 5. Insert data
# ----------------------------
print("Inserting data into MongoDB...")
start_time = time.time()
collection.insert_many(data)
end_time = time.time()
print(f"Data inserted successfully in {end_time - start_time:.2f} seconds")

# ----------------------------
# 6. Create indexes
# ----------------------------
print("Creating indexes...")
collection.create_index("forklift_id")
collection.create_index("timestamp")
collection.create_index("shift")
collection.create_index("zone")
collection.create_index("status")
collection.create_index("downtime_category")
print("Indexes created successfully")

# ----------------------------
# 7. Verify count
# ----------------------------
count = collection.count_documents({})
print(f"Total documents in collection: {count}")

print("MongoDB setup completed successfully")