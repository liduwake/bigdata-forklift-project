import pandas as pd
import matplotlib.pyplot as plt
import os

# ================================
# Configuration
# ================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "output", "forklift_dataset.csv")
OUTPUT_DIR = "output"

# ================================
# Load Data
# ================================
df = pd.read_csv(DATA_PATH)

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("Dataset loaded:", df.shape)

print("\nUnique values in status column:")
print(df["status"].dropna().unique())

print("\nUnique values in downtime_category column:")
print(df["downtime_category"].dropna().unique())

# ================================
# 1. Downtime Distribution
# ================================
category_counts = df["downtime_category"].value_counts()

plt.figure(figsize=(12, 7))
category_counts.plot(kind="bar")

plt.title("Distribution of Downtime Categories")
plt.xlabel("Downtime Category")
plt.ylabel("Count")
plt.xticks(rotation=35, ha="right")
plt.tight_layout()

plt.savefig(f"{OUTPUT_DIR}/chart_downtime.png", dpi=300, bbox_inches="tight")
print("Saved: chart_downtime.png")

# ================================
# 2. Zone Activity
# ================================
zone_counts = df["zone"].value_counts()

plt.figure(figsize=(10, 6))
zone_counts.plot(kind="bar")

plt.title("Forklift Activity by Zone")
plt.xlabel("Zone")
plt.ylabel("Number of Events")
plt.xticks(rotation=20, ha="right")
plt.tight_layout()

plt.savefig(f"{OUTPUT_DIR}/chart_zone.png", dpi=300, bbox_inches="tight")
print("Saved: chart_zone.png")

# ================================
# 3. Shift vs Status
# ================================
shift_status = pd.crosstab(df["shift"], df["status"])

if shift_status.empty:
    print("Warning: shift vs status table is empty, chart not generated.")
else:
    ax = shift_status.plot(kind="bar", stacked=True, figsize=(10, 6))
    ax.set_title("Forklift Status Distribution by Shift")
    ax.set_xlabel("Shift")
    ax.set_ylabel("Count")
    plt.xticks(rotation=0)
    plt.tight_layout()

    plt.savefig(f"{OUTPUT_DIR}/chart_shift_status.png", dpi=300, bbox_inches="tight")
    print("Saved: chart_shift_status.png")

# ================================
# 4. Top Unauthorized Forklifts
# ================================
top_forklifts = (
    df[df["downtime_category"] == "unauthorized_operation"]["forklift_id"]
    .value_counts()
    .head(5)
)

if top_forklifts.empty:
    print("Warning: No unauthorized_operation records found in downtime_category column.")
else:
    plt.figure(figsize=(9, 6))
    top_forklifts.plot(kind="bar")

    plt.title("Top 5 Forklifts with Unauthorized Operations")
    plt.xlabel("Forklift ID")
    plt.ylabel("Count")
    plt.xticks(rotation=0)
    plt.tight_layout()

    plt.savefig(f"{OUTPUT_DIR}/chart_top_forklifts.png", dpi=300, bbox_inches="tight")
    print("Saved: chart_top_forklifts.png")

print("\nAll charts generated successfully!")
