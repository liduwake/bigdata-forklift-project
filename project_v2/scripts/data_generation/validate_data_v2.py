import pandas as pd
from datetime import datetime
# Load dataset
df = pd.read_csv("../output/forklift_dataset.csv")

# Prepare report content
report = []

current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

report.append("=== DATA VALIDATION REPORT ===")
report.append(f"Generated at: {current_time}\n")

# Basic info
report.append(f"Dataset shape: {df.shape}\n")
report.append(f"Columns: {df.columns.tolist()}\n")

# Missing values
report.append("\n=== Missing Values ===")
report.append(str(df.isnull().sum()))

# Distributions
report.append("\n=== Shift Distribution ===")
report.append(str(df["shift"].value_counts()))

report.append("\n=== Status Distribution ===")
report.append(str(df["status"].value_counts()))

report.append("\n=== Downtime Category Distribution ===")
report.append(str(df["downtime_category"].value_counts()))

report.append("\n=== Visible Distribution ===")
report.append(str(df["visible"].value_counts()))

report.append("\n=== MOV Distribution ===")
report.append(str(df["mov"].value_counts()))

report.append("\n=== OCC Distribution ===")
report.append(str(df["occ"].value_counts()))

report.append("\n=== Zone Distribution ===")
report.append(str(df["zone"].value_counts()))

# Logical checks
report.append("\n=== Logical Checks ===")

offline_visible = df[(df["status"] == "offline") & (df["visible"] == 1)].shape[0]
report.append(f"offline but visible = 1: {offline_visible}")

visible_rssi = df[(df["visible"] == 0) & (df["rssi"] != 0)].shape[0]
report.append(f"visible = 0 but rssi != 0: {visible_rssi}")

mov_occ = df[(df["mov"] == 1) & (df["occ"] == 0)].shape[0]
report.append(f"mov = 1 and occ = 0 (unauthorized/anomaly): {mov_occ}")

# Save to file
output_path = "../output/data_validation_report.txt"

with open(output_path, "w", encoding="utf-8") as f:
    for line in report:
        f.write(line + "\n")

print(f"\nReport saved to: {output_path}")