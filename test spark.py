import os
import sys

python_exe = sys.executable
os.environ["PYSPARK_PYTHON"] = python_exe
os.environ["PYSPARK_DRIVER_PYTHON"] = python_exe

from pyspark.sql import SparkSession

print("Python executable:", python_exe)
print("PYSPARK_PYTHON:", os.environ.get("PYSPARK_PYTHON"))
print("PYSPARK_DRIVER_PYTHON:", os.environ.get("PYSPARK_DRIVER_PYTHON"))

spark = (
    SparkSession.builder
    .appName("VSCodeSparkTest")
    .master("local[1]")
    .config("spark.pyspark.python", python_exe)
    .config("spark.pyspark.driver.python", python_exe)
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")

rdd = spark.sparkContext.parallelize([1, 2, 3, 4, 5], 1)
print("RDD:", rdd.collect())
print("Count:", rdd.count())

spark.stop()