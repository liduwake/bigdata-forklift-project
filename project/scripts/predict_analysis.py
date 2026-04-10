import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, sum as spark_sum, when, round

# -----------------------------
# 1. Initialize Spark
# -----------------------------
spark = SparkSession.builder \
    .appName("Forklift Predict Analysis") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

# -----------------------------
# 2. Resolve Paths
# -----------------------------
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
file_path = os.path.join(base_dir, "data", "forklift_dataset.csv")
output_path = os.path.join(base_dir, "output", "spark_results")

os.makedirs(output_path, exist_ok=True)

print("Loading file from:", file_path)
print("Saving results to:", output_path)

# -----------------------------
# 3. Load Dataset
# -----------------------------
df = spark.read.csv(file_path, header=True, inferSchema=True)

# -----------------------------
# 4. Forklift Downtime Ranking
# -----------------------------
downtime_by_forklift = df.groupBy("forklift_id") \
    .agg(
        count("*").alias("total_records"),
        spark_sum(
            when(col("downtime_category") != "active_work", 1).otherwise(0)
        ).alias("downtime_count")
    ) \
    .withColumn(
        "downtime_rate",
        round(col("downtime_count") / col("total_records"), 4)
    ) \
    .orderBy(col("downtime_rate").desc())

downtime_by_forklift.toPandas().to_csv(
    os.path.join(output_path, "predict_downtime_by_forklift.csv"),
    index=False
)

# -----------------------------
# 5. Offline Risk (Forklift + Shift)
# -----------------------------
offline_risk = df.groupBy("forklift_id", "shift") \
    .agg(
        count("*").alias("total_records"),
        spark_sum(
            when(col("status") == "offline", 1).otherwise(0)
        ).alias("offline_count")
    ) \
    .withColumn(
        "offline_rate",
        round(col("offline_count") / col("total_records"), 4)
    ) \
    .orderBy(col("offline_rate").desc())

offline_risk.toPandas().to_csv(
    os.path.join(output_path, "predict_offline_risk.csv"),
    index=False
)

# -----------------------------
# 6. Unauthorized Risk (Forklift + Shift)
# -----------------------------
unauthorized_risk = df.groupBy("forklift_id", "shift") \
    .agg(
        count("*").alias("total_records"),
        spark_sum(
            when(col("downtime_category") == "unauthorized_operation", 1).otherwise(0)
        ).alias("unauthorized_count")
    ) \
    .withColumn(
        "unauthorized_rate",
        round(col("unauthorized_count") / col("total_records"), 4)
    ) \
    .orderBy(col("unauthorized_rate").desc())

unauthorized_risk.toPandas().to_csv(
    os.path.join(output_path, "predict_unauthorized_risk.csv"),
    index=False
)

# -----------------------------
# 7. Composite Risk (Zone + Shift)
# -----------------------------
composite_risk = df.groupBy("zone", "shift") \
    .agg(
        count("*").alias("total_records"),
        spark_sum(
            when(col("status") == "offline", 1).otherwise(0)
        ).alias("offline_count"),
        spark_sum(
            when(col("downtime_category") == "unauthorized_operation", 1).otherwise(0)
        ).alias("unauthorized_count")
    ) \
    .withColumn(
        "total_risk_events",
        col("offline_count") + col("unauthorized_count")
    ) \
    .withColumn(
        "risk_score",
        round(col("total_risk_events") / col("total_records"), 4)
    ) \
    .orderBy(col("risk_score").desc())

composite_risk.toPandas().to_csv(
    os.path.join(output_path, "predict_composite_risk_zone_shift.csv"),
    index=False
)

# -----------------------------
# 8. Zone Risk Only
# -----------------------------
zone_risk = df.groupBy("zone") \
    .agg(
        count("*").alias("total_records"),
        spark_sum(
            when(col("status") == "offline", 1).otherwise(0)
        ).alias("offline_count")
    ) \
    .withColumn(
        "offline_rate",
        round(col("offline_count") / col("total_records"), 4)
    ) \
    .orderBy(col("offline_rate").desc())

zone_risk.toPandas().to_csv(
    os.path.join(output_path, "predict_zone_risk.csv"),
    index=False
)

# -----------------------------
# 9. Shift Risk Only
# -----------------------------
shift_risk = df.groupBy("shift") \
    .agg(
        count("*").alias("total_records"),
        spark_sum(
            when(col("status") == "offline", 1).otherwise(0)
        ).alias("offline_count")
    ) \
    .withColumn(
        "offline_rate",
        round(col("offline_count") / col("total_records"), 4)
    ) \
    .orderBy(col("offline_rate").desc())

shift_risk.toPandas().to_csv(
    os.path.join(output_path, "predict_shift_risk.csv"),
    index=False
)

print("Predict analysis completed successfully.")
print("Files saved:")
print("- predict_downtime_by_forklift.csv")
print("- predict_offline_risk.csv")
print("- predict_unauthorized_risk.csv")
print("- predict_composite_risk_zone_shift.csv")
print("- predict_zone_risk.csv")
print("- predict_shift_risk.csv")

spark.stop()