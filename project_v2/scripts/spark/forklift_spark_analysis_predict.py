import os
import time
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    avg,
    to_timestamp,
    when,
    count,
    sum as spark_sum,
    round
)

# =========================
# SETUP
# =========================
output_dir = "../output/spark_results"
os.makedirs(output_dir, exist_ok=True)

start_total = time.time()

spark = SparkSession.builder \
    .appName("Forklift Big Data Analysis with Prediction") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

# =========================
# LOAD DATA
# =========================
start_load = time.time()

df = spark.read.csv(
    "../output/forklift_dataset.csv",
    header=True,
    inferSchema=True
)

df = df.withColumn("timestamp", to_timestamp(col("timestamp")))

# Cache for repeated analysis
df.cache()
df.count()

end_load = time.time()

# =========================
# BASIC INFO
# =========================
schema_str = df._jdf.schema().treeString()
total_records = df.count()
total_columns = len(df.columns)

# =========================
# DATAFRAME API ANALYSIS
# =========================
start_transform = time.time()

category_counts = df.groupBy("downtime_category") \
    .count() \
    .orderBy(col("count").desc())

shift_counts = df.groupBy("shift") \
    .count() \
    .orderBy("shift")

zone_counts = df.groupBy("zone") \
    .count() \
    .orderBy(col("count").desc())

status_counts = df.groupBy("status") \
    .count()

avg_rssi_by_zone = df.filter(col("visible") == 1) \
    .groupBy("zone") \
    .agg(avg("rssi").alias("avg_rssi")) \
    .orderBy(col("avg_rssi").asc())

active_work_by_forklift = df.filter(col("downtime_category") == "active_work") \
    .groupBy("forklift_id") \
    .count() \
    .orderBy(col("count").desc())

unauthorized_by_forklift = df.filter(col("downtime_category") == "unauthorized_operation") \
    .groupBy("forklift_id") \
    .count() \
    .orderBy(col("count").desc())

end_transform = time.time()

# =========================
# SIMPLE PREDICTIVE ANALYSIS
# =========================
start_predict = time.time()

# 1. Predict offline risk by forklift and shift
offline_risk_by_forklift_shift = df.groupBy("forklift_id", "shift") \
    .agg(
        count("*").alias("total_records"),
        spark_sum(when(col("status") == "offline", 1).otherwise(0)).alias("offline_count")
    ) \
    .withColumn(
        "offline_risk",
        round(col("offline_count") / col("total_records"), 4)
    ) \
    .orderBy(col("offline_risk").desc())

# 2. Predict unauthorized operation risk by forklift and shift
unauthorized_risk_by_forklift_shift = df.groupBy("forklift_id", "shift") \
    .agg(
        count("*").alias("total_records"),
        spark_sum(
            when(col("downtime_category") == "unauthorized_operation", 1).otherwise(0)
        ).alias("unauthorized_count")
    ) \
    .withColumn(
        "unauthorized_risk",
        round(col("unauthorized_count") / col("total_records"), 4)
    ) \
    .orderBy(col("unauthorized_risk").desc())

# 3. Predict offline risk by zone and shift
offline_risk_by_zone_shift = df.groupBy("zone", "shift") \
    .agg(
        count("*").alias("total_records"),
        spark_sum(when(col("status") == "offline", 1).otherwise(0)).alias("offline_count")
    ) \
    .withColumn(
        "offline_risk",
        round(col("offline_count") / col("total_records"), 4)
    ) \
    .orderBy(col("offline_risk").desc())

end_predict = time.time()

# =========================
# SPARK SQL ANALYSIS
# =========================
start_sql = time.time()

df.createOrReplaceTempView("forklift_data")

zone_shift_summary = spark.sql("""
    SELECT
        zone,
        shift,
        COUNT(*) AS record_count,
        ROUND(AVG(rssi), 2) AS avg_rssi
    FROM forklift_data
    WHERE visible = 1
    GROUP BY zone, shift
    ORDER BY zone, shift
""")

offline_summary = spark.sql("""
    SELECT
        shift,
        COUNT(*) AS offline_count
    FROM forklift_data
    WHERE status = 'offline'
    GROUP BY shift
    ORDER BY shift
""")

# SQL-based predictive summary
offline_prediction_sql = spark.sql("""
    SELECT
        forklift_id,
        shift,
        COUNT(*) AS total_records,
        SUM(CASE WHEN status = 'offline' THEN 1 ELSE 0 END) AS offline_count,
        ROUND(
            SUM(CASE WHEN status = 'offline' THEN 1 ELSE 0 END) / COUNT(*),
            4
        ) AS predicted_offline_risk
    FROM forklift_data
    GROUP BY forklift_id, shift
    ORDER BY predicted_offline_risk DESC
""")

end_sql = time.time()

# =========================
# SAVE RESULTS
# =========================
start_save = time.time()

category_counts.toPandas().to_csv(f"{output_dir}/category_counts.csv", index=False)
shift_counts.toPandas().to_csv(f"{output_dir}/shift_counts.csv", index=False)
zone_counts.toPandas().to_csv(f"{output_dir}/zone_counts.csv", index=False)
status_counts.toPandas().to_csv(f"{output_dir}/status_counts.csv", index=False)
avg_rssi_by_zone.toPandas().to_csv(f"{output_dir}/avg_rssi_by_zone.csv", index=False)
active_work_by_forklift.toPandas().to_csv(f"{output_dir}/active_work_by_forklift.csv", index=False)
unauthorized_by_forklift.toPandas().to_csv(f"{output_dir}/unauthorized_by_forklift.csv", index=False)

zone_shift_summary.toPandas().to_csv(f"{output_dir}/spark_sql_zone_shift_summary.csv", index=False)
offline_summary.toPandas().to_csv(f"{output_dir}/spark_sql_offline_summary.csv", index=False)
offline_prediction_sql.toPandas().to_csv(f"{output_dir}/spark_sql_offline_prediction.csv", index=False)

offline_risk_by_forklift_shift.toPandas().to_csv(
    f"{output_dir}/offline_risk_by_forklift_shift.csv", index=False
)
unauthorized_risk_by_forklift_shift.toPandas().to_csv(
    f"{output_dir}/unauthorized_risk_by_forklift_shift.csv", index=False
)
offline_risk_by_zone_shift.toPandas().to_csv(
    f"{output_dir}/offline_risk_by_zone_shift.csv", index=False
)

end_save = time.time()
end_total = time.time()

# =========================
# WRITE EXECUTION REPORT
# =========================
report_path = f"{output_dir}/spark_execution_report.txt"

with open(report_path, "w", encoding="utf-8") as f:
    f.write("=== SPARK EXECUTION REPORT ===\n\n")
    f.write(f"Total records: {total_records}\n")
    f.write(f"Total columns: {total_columns}\n\n")

    f.write("=== SCHEMA ===\n")
    f.write(schema_str + "\n\n")

    f.write("=== TIMING (seconds) ===\n")
    f.write(f"Load and cache time: {end_load - start_load:.4f}\n")
    f.write(f"Transformation time: {end_transform - start_transform:.4f}\n")
    f.write(f"Predictive analysis time: {end_predict - start_predict:.4f}\n")
    f.write(f"SQL query time: {end_sql - start_sql:.4f}\n")
    f.write(f"Save results time: {end_save - start_save:.4f}\n")
    f.write(f"Total execution time: {end_total - start_total:.4f}\n\n")

    f.write("=== OUTPUT FILES ===\n")
    f.write("category_counts.csv\n")
    f.write("shift_counts.csv\n")
    f.write("zone_counts.csv\n")
    f.write("status_counts.csv\n")
    f.write("avg_rssi_by_zone.csv\n")
    f.write("active_work_by_forklift.csv\n")
    f.write("unauthorized_by_forklift.csv\n")
    f.write("spark_sql_zone_shift_summary.csv\n")
    f.write("spark_sql_offline_summary.csv\n")
    f.write("spark_sql_offline_prediction.csv\n")
    f.write("offline_risk_by_forklift_shift.csv\n")
    f.write("unauthorized_risk_by_forklift_shift.csv\n")
    f.write("offline_risk_by_zone_shift.csv\n")

print("Spark analysis with prediction completed successfully.")
print(f"Results saved to: {output_dir}")
print(f"Execution report saved to: {report_path}")

spark.stop()