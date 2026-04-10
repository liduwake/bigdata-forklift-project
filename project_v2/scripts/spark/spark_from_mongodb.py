from pymongo import MongoClient
from pyspark.sql import SparkSession

# MongoDB Atlas config
MONGO_URI = "mongodb+srv://liduwake_db_user:5kZPKAqztPvIBihe@cluster0.0bxt6ih.mongodb.net/?appName=Cluster0"
DB_NAME = "forklift_project_v2"
COLLECTION_NAME = "forklift_raw"

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

print("Connecting to MongoDB Atlas...")
sample_count = collection.count_documents({})
print(f"Connected successfully. Total documents in collection: {sample_count}")

# Read data from MongoDB
mongo_docs = list(collection.find({}, {"_id": 0}))
print(f"Loaded {len(mongo_docs)} records from MongoDB.")

# Start Spark session
spark = SparkSession.builder \
    .appName("MongoDB_to_Spark") \
    .master("local[*]") \
    .getOrCreate()

# Convert to Spark DataFrame
df = spark.createDataFrame(mongo_docs)

print("Spark schema:")
df.printSchema()

print("Sample rows:")
df.show(5, truncate=False)

# Basic Spark analysis
print("Status count:")
df.groupBy("status").count().show()

print("Downtime category count:")
df.groupBy("downtime_category").count().show()

# Spark SQL
df.createOrReplaceTempView("forklift_data")

print("Spark SQL result:")
spark.sql("""
    SELECT shift, status, COUNT(*) AS cnt
    FROM forklift_data
    GROUP BY shift, status
    ORDER BY shift, cnt DESC
""").show()

spark.stop()