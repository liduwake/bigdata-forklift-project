import os
import time
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, to_timestamp

# =========================
# SETUP
# =========================
output_dir = "../output/spark_results"
os.makedirs(output_dir, exist_ok=True)

start_total = time.time()

# Create Spark session
spark = SparkSession.builder \
    .appName("Forklift Big Data Analysis") \
    .getOrCreate()

# Reduce console noise
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

# Cache dataset for repeated analysis
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

unauthorized_by_forklift = df.filter((col("mov") == 1) & (col("occ") == 0)) \
    .groupBy("forklift_id") \
    .count() \
    .orderBy(col("count").desc())

end_transform = time.time()

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

end_sql = time.time()

# =========================
# SAVE RESULTS WITH PANDAS
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

print("Spark analysis completed successfully.")
print(f"Results saved to: {output_dir}")
print(f"Execution report saved to: {report_path}")

spark.stop()