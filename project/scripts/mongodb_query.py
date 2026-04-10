import os
import sys
import time
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
# 2. Show one sample document
# ----------------------------
sample_doc = collection.find_one()
print("\nSample document:")
print(sample_doc)

# ----------------------------
# 3. Show all field names
# ----------------------------
if sample_doc:
    print("\nDetected fields:")
    print(list(sample_doc.keys()))

# ----------------------------
# 4. Query 1: total document count
# ----------------------------
start_time = time.time()
total_count = collection.count_documents({})
end_time = time.time()

print("\nQuery 1: Total document count")
print("Total documents:", total_count)
print(f"Query time: {end_time - start_time:.4f} seconds")

# ----------------------------
# 5. Query 2: top 5 documents sorted by forklift_id
# ----------------------------
start_time = time.time()
results = list(collection.find({}, {"_id": 0}).sort("forklift_id", 1).limit(5))
end_time = time.time()

print("\nQuery 2: Top 5 documents sorted by forklift_id")
for doc in results:
    print(doc)
print(f"Query time: {end_time - start_time:.4f} seconds")

# ----------------------------
# 6. Aggregation 1: record count by shift
# ----------------------------
start_time = time.time()
pipeline = [
    {"$group": {"_id": "$shift", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}}
]
results = list(collection.aggregate(pipeline))
end_time = time.time()

print("\nAggregation 1: Record count by shift")
for doc in results:
    print(doc)
print(f"Query time: {end_time - start_time:.4f} seconds")

# ----------------------------
# 7. Aggregation 2: record count by zone
# ----------------------------
start_time = time.time()
pipeline = [
    {"$group": {"_id": "$zone", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}}
]
results = list(collection.aggregate(pipeline))
end_time = time.time()

print("\nAggregation 2: Record count by zone")
for doc in results:
    print(doc)
print(f"Query time: {end_time - start_time:.4f} seconds")

# ----------------------------
# 8. Aggregation 3: top 5 forklifts by record count
# ----------------------------
start_time = time.time()
pipeline = [
    {"$group": {"_id": "$forklift_id", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}},
    {"$limit": 5}
]
results = list(collection.aggregate(pipeline))
end_time = time.time()

print("\nAggregation 3: Top 5 forklifts by record count")
for doc in results:
    print(doc)
print(f"Query time: {end_time - start_time:.4f} seconds")

# ----------------------------
# 9. Aggregation 4: offline count by shift
# ----------------------------
start_time = time.time()
pipeline = [
    {"$match": {"status": "offline"}},
    {"$group": {"_id": "$shift", "offline_count": {"$sum": 1}}},
    {"$sort": {"offline_count": -1}}
]
results = list(collection.aggregate(pipeline))
end_time = time.time()

print("\nAggregation 4: Offline count by shift")
for doc in results:
    print(doc)
print(f"Query time: {end_time - start_time:.4f} seconds")

# ----------------------------
# 10. Aggregation 5: unauthorized_operation by forklift
# ----------------------------
start_time = time.time()
pipeline = [
    {"$match": {"downtime_category": "unauthorized_operation"}},
    {"$group": {"_id": "$forklift_id", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}},
    {"$limit": 5}
]
results = list(collection.aggregate(pipeline))
end_time = time.time()

print("\nAggregation 5: Top 5 forklifts by unauthorized_operation")
for doc in results:
    print(doc)
print(f"Query time: {end_time - start_time:.4f} seconds")

# ----------------------------
# 11. Following project requirements, comparing performance with Spark and MongoDB Aggregation Framework
# ----------------------------

print("MongoDB aggregation execution time:", round(end_time - start_time, 4), "seconds")
print(results)
print("\nMongoDB query completed successfully")