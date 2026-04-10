import os
import pandas as pd

# Get project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "output", "forklift_dataset.csv")

df = pd.read_csv(DATA_PATH)

unauth_counts = (
    df[df["downtime_category"] == "unauthorized_operation"]["forklift_id"]
    .value_counts()
    .sort_values(ascending=False)
)

print(unauth_counts.head(10))
print("\nMin:", unauth_counts.min())
print("Max:", unauth_counts.max())
print("Std:", unauth_counts.std())
# ================================
# Check 2: Shift vs Status
# ================================
print("\n=== Shift vs Status (Raw Counts) ===")
shift_status = pd.crosstab(df["shift"], df["status"])
print(shift_status)

print("\n=== Shift vs Status (Normalized by row) ===")
shift_status_norm = pd.crosstab(df["shift"], df["status"], normalize="index")
print(shift_status_norm)