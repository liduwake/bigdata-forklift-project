# 🚀 Big Data Forklift Analysis Project

## 📌 Overview

This project simulates and analyzes industrial forklift operations using a complete big data pipeline.

Unlike typical projects that use existing datasets, this project **generates synthetic data based on realistic operational assumptions**, and then processes it using Spark and MongoDB.

The pipeline includes:

- Data generation  
- Data validation  
- Spark processing  
- MongoDB storage and sharding  
- Predictive analysis  
- Visualization  

---

## 🔄 Pipeline Evolution (Version 1 → Version 2)

During the development process, the project evolved into two versions:

### Version 1 (Baseline Pipeline) in project folder
- Data is generated and stored in MongoDB
- Data is processed using Spark
- MongoDB is used as a centralized storage system

### Version 2 (Optimized Sharded Pipeline) in project_v2 folder
- Data is generated and directly uploaded into a **MongoDB sharded cluster**
- Data is distributed across multiple shards (shardA and shardB)
- The system connects through **mongos (port 27120)**
- Designed to simulate **scalable big data architecture**

This improvement demonstrates how a basic pipeline can be extended into a more scalable system.

---

## 🧱 Project Structure

```
project/
│
├── config/                  
├── scripts/
│   ├── data_generation/     
│   ├── spark/               
│   ├── mongodb/             
│   ├── prediction/          
│   └── testing/             
│
├── visualization/           
├── output/                  
├── data/        (not included)  
├── sharding/   (not included)
```

---

# 📊 Data Generation (Core Design)

This project uses **synthetic data generation** to simulate forklift operations.

## 🔧 Key Idea

Instead of random data, the dataset is generated using **probability-based rules** that reflect real industrial behavior.

---

## 🧠 Simulation Logic

### 1️⃣ Shift-Based Behavior

Different shifts have different risk levels:

- Morning → stable, lower risk  
- Afternoon → moderate activity  
- Night → higher probability of downtime and errors  

Example logic:

```
Night shift → higher probability of:
- signal_loss_or_offline
- unauthorized_operation
```

---

### 2️⃣ Zone-Based Differences

Each zone has different operational characteristics:

- WIP (Work In Progress) → high movement, high complexity  
- Packing → high workload pressure  
- Storage → relatively stable  
- Charging → low activity  

---

### 3️⃣ Combined Risk Modeling

The dataset includes combined effects:

```
Zone + Shift → affects downtime probability
```

Example:

- WIP + Night → highest risk  
- Packing + Night → elevated risk  
- Production + Morning → low risk  

---

### 4️⃣ Data Features

Each record includes:

- timestamp  
- forklift_id  
- zone  
- shift  
- rssi (signal strength)  
- movement status  
- visibility  
- downtime_category  

---

## ⚠️ Dataset Note

The dataset (~288,000 rows) is not included due to size limitations.

It can be regenerated using:

```bash
python scripts/data_generation/generate_data.py
```

---

# ⚙️ How to Run 

Version 1 (Baseline Pipeline)

## 1️⃣ Generate Data

```bash
python scripts/data_generation/generate_data.py
```

## 2️⃣ Validate Data

```bash
python scripts/data_generation/validate_data.py
```

## 3️⃣ Run Spark Analysis

```bash
python scripts/spark/spark_analysis.py
```

## 4️⃣ MongoDB Integration

```bash
python scripts/mongodb/mongodb_integration.py
```

## 5️⃣ MongoDB Queries

```bash
python scripts/mongodb/mongodb_query.py
```

## 6️⃣ Predictive Analysis

```bash
python scripts/prediction/predict_analysis.py
```

## 7️⃣ Visualization

```bash
python visualization/generate_charts.py
```

🔹 Version 2 (Sharded Cluster Pipeline)

⚠️ Version 2 requires MongoDB Sharding environment to be running
1️⃣ Start MongoDB Sharding Cluster

Run PowerShell scripts (example):

# Start config server
mongod --configsvr --replSet configReplSet --port 27019 --dbpath D:\mongo\config

# Start shard A
mongod --shardsvr --replSet shardA --port 27018 --dbpath D:\mongo\shardA

# Start shard B
mongod --shardsvr --replSet shardB --port 27028 --dbpath D:\mongo\shardB

# Start mongos router
mongos --configdb configReplSet/localhost:27019 --port 27120

2️⃣ Initialize Sharding (One-time setup)

Inside mongo shell:

sh.addShard("shardA/localhost:27018")
sh.addShard("shardB/localhost:27028")

sh.enableSharding("your_database")
sh.shardCollection("your_database.your_collection", { forklift_id: "hashed" })
3️⃣ Run Data Generation
python scripts/data_generation/generate_data.py
4️⃣ Upload Data to Sharded Cluster

⚠️ 注意：这里必须连接 mongos（27120）

python scripts/mongodb/mongodb_integration.py
5️⃣ Verify Sharding
sh.status()

Expected:

Data split across shardA and shardB
Balanced distribution
6️⃣ Run Queries (Same as V1)
python scripts/mongodb/mongodb_query.py
7️⃣ Spark Analysis (Optional but recommended)
python scripts/spark/spark_analysis.py
8️⃣ Visualization
python visualization/generate_charts.py
▶️ Quick Start
🔹 Version 1 (Simple)
python scripts/data_generation/generate_data.py
python scripts/spark/spark_analysis.py
python visualization/generate_charts.py
🔹 Version 2 (Sharded)
# 1. Start MongoDB Sharding cluster
# 2. Run data pipeline

python scripts/data_generation/generate_data.py
python scripts/mongodb/mongodb_integration.py
python scripts/mongodb/mongodb_query.py

---

# 🧠 MongoDB Sharding (Version 2 Enhancement)

In the optimized pipeline (Version 2), MongoDB sharding is implemented to simulate scalable big data systems.

## ⚙️ Architecture

- Config Server
- Mongos Router (port 27120)
- Two shards:
  - shardA
  - shardB

## 🔄 Data Flow

Python scripts do NOT implement sharding directly.

Instead:

- Sharding is configured at the database level using cluster setup scripts
- Python connects to the cluster via **mongos**
- MongoDB automatically distributes data across shards

## 📊 Distribution Result

Data is evenly distributed:

```
shardA → ~144,000 documents  
shardB → ~144,000 documents  
```

## Insight

Sharding enables:

- Horizontal scaling  
- Parallel processing  
- Improved performance  
This reflects a real-world distributed database design.
---

# 📈 Predictive Analysis

The project applies **pattern-based predictive analysis** using historical data.

Instead of complex machine learning, we use:

- Aggregation  
- Grouping  
- Multi-factor analysis  

Key factors:

- Zone  
- Shift  
- Downtime category  

---

# 📊 Visualization

Visualization is implemented using Python scripts.

Charts include:

- Downtime distribution  
- Shift-based analysis  
- Zone comparison  
- Risk comparison  

Purpose:

- Identify patterns  
- Compare operational conditions  
- Support decision-making  

---

# 🔍 Key Insights

- WIP zone during night shift shows the highest risk  
- Packing zone also has elevated risk at night  
- Daytime shifts are more stable  

---


# 📌 Notes

- This project focuses on **data pipeline and system design**  
- Synthetic data is designed to reflect real-world behavior  
- All results are reproducible  

---

# 🔧 Requirements

- Python 3.x  
- PySpark  
- MongoDB  
- pandas  

---

# ▶️ Quick Start

```bash
# Step 1: Generate data
python scripts/data_generation/generate_data.py

# Step 2: Run analysis
python scripts/spark/spark_analysis.py

# Step 3: Visualize results
python visualization/generate_charts.py
```
## ⚠️ Script Execution Note (Important)

During development, scripts were reorganized into subfolders based on functionality.

However, some scripts were originally written using relative paths. After moving them into subfolders, certain scripts may not run correctly without modifying those paths.

Therefore:

- The main runnable scripts are still in the root `scripts/` folder  
- Subfolder scripts are mainly for organization and review  
- Subfolder scripts are not guaranteed to run directly  

---

# ⚡ Spark SQL, MongoDB Comparison, and Optimization Updates

During the latest stage of the project, several additional improvements were completed to better match the course requirements and bonus tasks.

## ✅ Spark SQL and MongoDB Aggregation Comparison

To satisfy the requirement of comparing **Spark SQL** with **MongoDB Aggregation Framework**, we implemented the same analytical query in both systems.

### Query Task

Top 5 forklifts with the highest number of `unauthorized_operation` records.

### Spark SQL Result

- Spark SQL query executed successfully
- Execution time: **0.74 seconds**

### MongoDB Aggregation Result

- MongoDB aggregation query executed successfully
- Execution time: **0.0874 seconds**

### Comparison Insight

In this local experiment, **MongoDB was faster** than Spark SQL for this focused query. This is reasonable because:

- MongoDB used indexed fields
- the dataset size is still moderate
- Spark has additional framework overhead in local execution

This shows:

- **MongoDB** is suitable for targeted indexed queries
- **Spark** is more useful for broader batch analytics and large-scale data processing

### Evidence

![result](images/spark_vs_mongodb.png)

---

## ⚙️ Spark Optimization

To improve Spark execution quality, the data pipeline was optimized with:

- **repartition before caching**
- **cache for repeated analysis**
- one `count()` action to materialize the cached DataFrame

This makes the Spark workflow more efficient and more technically sound for repeated analysis tasks.

---

## 📦 CSV vs Parquet Comparison

As an additional optimization experiment, we compared Spark reading performance between **CSV** and **Parquet** formats.

### Result

- CSV read time: **1.3908 seconds**
- Parquet read time: **1.3116 seconds**



### Interpretation

The difference was small, which is reasonable because:

- the dataset is not extremely large
- the experiment was run in a local environment
- Spark overhead is still significant at this scale

Even so, **Parquet was slightly faster**, which still supports the value of storage format optimization.

### Evidence

![result](images/CSV_VS_Parquet.png)

---

## 📊 Interactive Dashboard

A simple interactive dashboard was built using **Streamlit**.

The dashboard presents:

- Top forklifts
- Status distribution
- Zone distribution

This improves result presentation and supports the bonus requirement for building an interactive dashboard.

### Evidence

![Streamlit dashboard](images/streamlit_dashboard.png)

---

## ⚠️ Script Execution Note (Important)

During development, scripts were documented into subfolders based on functionality for easy readability.

However, some scripts were originally written using relative paths. After moving them into subfolders, certain scripts may not run correctly without modifying those paths.

Therefore:

- The main runnable scripts are still in the root `scripts/` folder  
- Subfolder scripts are mainly for organization and review  
- Subfolder scripts are not guaranteed to run directly  

