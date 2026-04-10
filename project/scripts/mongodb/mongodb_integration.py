import pandas as pd
from pymongo import MongoClient
from datetime import datetime

# =========================
# CONFIGURATION
# =========================
MONGO_URI = "mongodb+srv://liduwake_db_user:5kZPKAqztPvIBihe@cluster0.0bxt6ih.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

DB_NAME = "bigdata_forklift_project"
EVENTS_COLLECTION = "forklift_events"
RESULTS_COLLECTION = "analysis_results"

DATASET_PATH = "../output/forklift_dataset.csv"
REPORT_PATH = "../output/mongodb_integration_report.txt"

# =========================
# CONNECT TO MONGODB
# =========================
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

events_col = db[EVENTS_COLLECTION]
results_col = db[RESULTS_COLLECTION]

# Test connection explicitly
client.admin.command("ping")
print("Connected to MongoDB Atlas successfully.")

# =========================
# LOAD DATASET
# =========================
df = pd.read_csv(DATASET_PATH)

# Convert timestamp to string for stable insertion
df["timestamp"] = df["timestamp"].astype(str)

# =========================
# CLEAN PREVIOUS DATA
# =========================
events_col.delete_many({})
results_col.delete_many({})

# =========================
# INSERT EVENT DATA
# =========================
event_docs = df.to_dict(orient="records")
events_col.insert_many(event_docs)

# =========================
# CREATE INDEXES
# =========================
events_col.create_index("forklift_id")
events_col.create_index("zone")
events_col.create_index("shift")
events_col.create_index("downtime_category")
events_col.create_index("status")

# =========================
# RUN QUERIES
# =========================
active_work_count = events_col.count_documents({
    "downtime_category": "active_work"
})

unauthorized_count = events_col.count_documents({
    "downtime_category": "unauthorized_operation"
})

offline_count = events_col.count_documents({
    "status": "offline"
})

unauthorized_pipeline = [
    {"$match": {"downtime_category": "unauthorized_operation"}},
    {"$group": {"_id": "$forklift_id", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}},
    {"$limit": 5}
]
top_unauthorized = list(events_col.aggregate(unauthorized_pipeline))

zone_pipeline = [
    {"$group": {"_id": "$zone", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}}
]
zone_counts = list(events_col.aggregate(zone_pipeline))

# =========================
# STORE SUMMARY RESULTS
# =========================
summary_doc = {
    "report_type": "mongodb_summary",
    "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "total_records": len(df),
    "active_work_count": active_work_count,
    "unauthorized_count": unauthorized_count,
    "offline_count": offline_count,
    "top_unauthorized_forklifts": top_unauthorized,
    "zone_counts": zone_counts
}

results_col.insert_one(summary_doc)

# =========================
# WRITE LOCAL REPORT
# =========================
with open(REPORT_PATH, "w", encoding="utf-8") as f:
    f.write("=== MONGODB INTEGRATION REPORT ===\n")
    f.write(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

    f.write(f"Database: {DB_NAME}\n")
    f.write(f"Collection 1: {EVENTS_COLLECTION}\n")
    f.write(f"Collection 2: {RESULTS_COLLECTION}\n\n")

    f.write("=== INSERTION SUMMARY ===\n")
    f.write(f"Inserted event records: {len(df)}\n\n")

    f.write("=== INDEXES CREATED ===\n")
    f.write("forklift_id\n")
    f.write("zone\n")
    f.write("shift\n")
    f.write("downtime_category\n")
    f.write("status\n\n")

    f.write("=== QUERY RESULTS ===\n")
    f.write(f"Active work count: {active_work_count}\n")
    f.write(f"Unauthorized operation count: {unauthorized_count}\n")
    f.write(f"Offline count: {offline_count}\n\n")

    f.write("Top 5 forklifts by unauthorized operations:\n")
    for item in top_unauthorized:
        f.write(f"{item['_id']}: {item['count']}\n")

    f.write("\nZone activity counts:\n")
    for item in zone_counts:
        f.write(f"{item['_id']}: {item['count']}\n")

print("MongoDB integration completed successfully.")
print(f"Inserted records into collection: {EVENTS_COLLECTION}")
print(f"Summary inserted into collection: {RESULTS_COLLECTION}")
print(f"Local report saved to: {REPORT_PATH}")