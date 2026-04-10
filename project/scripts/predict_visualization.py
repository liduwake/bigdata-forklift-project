import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ================================
# Paths
# ================================
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_path = os.path.join(base_dir, "output", "spark_results")
chart_path = os.path.join(base_dir, "output")

print("Reading from:", data_path)
print("Saving charts to:", chart_path)

# ================================
# 1. Top Downtime Forklifts
# ================================
df = pd.read_csv(os.path.join(data_path, "predict_downtime_by_forklift.csv"))

top10 = df.head(10)

plt.figure(figsize=(10, 6))
plt.bar(top10["forklift_id"], top10["downtime_rate"])
plt.title("Top Downtime Forklifts")
plt.xlabel("Forklift ID")
plt.ylabel("Downtime Rate")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(chart_path, "chart_predict_downtime.png"), dpi=300, bbox_inches="tight")
plt.close()

# ================================
# 2. Composite Risk Heatmap
# ================================
df = pd.read_csv(os.path.join(data_path, "predict_composite_risk_zone_shift.csv"))

pivot = df.pivot(index="zone", columns="shift", values="risk_score")

plt.figure(figsize=(8, 6))
sns.heatmap(pivot, annot=True, fmt=".4f")
plt.title("Composite Risk (Zone + Shift)")
plt.tight_layout()
plt.savefig(os.path.join(chart_path, "chart_predict_composite_heatmap.png"), dpi=300, bbox_inches="tight")
plt.close()

# ================================
# 3. Offline Risk by Shift
# ================================
df = pd.read_csv(os.path.join(data_path, "predict_shift_risk.csv"))

plt.figure(figsize=(8, 6))
plt.bar(df["shift"], df["offline_rate"])
plt.title("Offline Risk by Shift")
plt.xlabel("Shift")
plt.ylabel("Offline Rate")
plt.tight_layout()
plt.savefig(os.path.join(chart_path, "chart_predict_shift.png"), dpi=300, bbox_inches="tight")
plt.close()

print("Predict visualization completed successfully.")
print("Saved charts:")
print("- chart_predict_downtime.png")
print("- chart_predict_composite_heatmap.png")
print("- chart_predict_shift.png")