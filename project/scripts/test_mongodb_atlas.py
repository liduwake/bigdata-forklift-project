import pandas as pd
from pymongo import MongoClient
import os

# ================================
# 1. MongoDB Connection
# ================================
MONGO_URI = "mongodb+srv://liduwake_db_user:5kZPKAqztPvIBihe@cluster0.0bxt6ih.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(MONGO_URI)

# 创建数据库
db = client["forklift_db"]

print("Connected to MongoDB Atlas successfully.")

# ================================
# 2. Path Setup
# ================================
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_path = os.path.join(base_dir, "output", "spark_results")

# ================================
# 3. Load Data
# ================================

# 1️⃣ downtime
df_downtime = pd.read_csv(os.path.join(data_path, "predict_downtime_by_forklift.csv"))

# 2️⃣ zone + shift risk
df_composite = pd.read_csv(os.path.join(data_path, "predict_composite_risk_zone_shift.csv"))

# 3️⃣ shift risk
df_shift = pd.read_csv(os.path.join(data_path, "predict_shift_risk.csv"))

print("CSV files loaded successfully.")

# ================================
# 4. Insert into MongoDB
# ================================

# Collection 1
collection1 = db["downtime_by_forklift"]
collection1.insert_many(df_downtime.to_dict("records"))

# Collection 2
collection2 = db["composite_risk"]
collection2.insert_many(df_composite.to_dict("records"))

# Collection 3
collection3 = db["shift_risk"]
collection3.insert_many(df_shift.to_dict("records"))

print("Data inserted into MongoDB.")

# ================================
# 5. Simple Query Test
# ================================

print("\nTop 3 forklifts by downtime:")

for doc in collection1.find().sort("downtime_rate", -1).limit(3):
    print(doc)

# ================================
# 6. Create Index (加分点🔥)
# ================================

collection1.create_index("forklift_id")
collection2.create_index([("zone", 1), ("shift", 1)])
collection3.create_index("shift")

print("Indexes created.")

# ================================
# 7. Close connection
# ================================

client.close()

print("MongoDB test completed.")