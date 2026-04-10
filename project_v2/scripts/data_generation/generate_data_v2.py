import os
import random
from datetime import datetime, timedelta

import pandas as pd
from pymongo import MongoClient

# =========================
# CONFIGURATION
# =========================
NUM_FORKLIFTS = 10
DAYS = 1
INTERVAL_SECONDS = 3
START_TIME = datetime(2026, 4, 1, 0, 0, 0)

# MongoDB config
MONGO_URI = "mongodb+srv://liduwake_db_user:5kZPKAqztPvIBihe@cluster0.0bxt6ih.mongodb.net/?appName=Cluster0"
DB_NAME = "forklift_project_v2"
RAW_COLLECTION_NAME = "forklift_raw"

# =========================
# ANCHOR / ZONE MAPPING
# =========================
ANCHOR_ZONE_MAP = {
    "A1": "Production",
    "A2": "Storage",
    "A3": "WIP",
    "A4": "Packing",
    "A5": "Production",
    "A6": "Charging",
    "A7": "Maintenance",
    "A8": "WIP",
}

ANCHORS = list(ANCHOR_ZONE_MAP.keys())

# =========================
# FORKLIFT PROFILE CONFIG
# =========================
FORKLIFT_PROFILES = {
    "FL_01": {
        "usage_level": "high",
        "risk_level": "high",
        "preferred_zones": ["Production", "WIP"],
    },
    "FL_02": {
        "usage_level": "high",
        "risk_level": "high",
        "preferred_zones": ["Production", "Storage"],
    },
    "FL_03": {
        "usage_level": "high",
        "risk_level": "medium",
        "preferred_zones": ["WIP", "Packing"],
    },
    "FL_04": {
        "usage_level": "medium",
        "risk_level": "medium",
        "preferred_zones": ["Storage", "Packing"],
    },
    "FL_05": {
        "usage_level": "medium",
        "risk_level": "low",
        "preferred_zones": ["Storage", "Charging"],
    },
    "FL_06": {
        "usage_level": "medium",
        "risk_level": "low",
        "preferred_zones": ["Production", "WIP"],
    },
    "FL_07": {
        "usage_level": "medium",
        "risk_level": "low",
        "preferred_zones": ["Packing", "Storage"],
    },
    "FL_08": {
        "usage_level": "low",
        "risk_level": "low",
        "preferred_zones": ["Charging", "Maintenance"],
    },
    "FL_09": {
        "usage_level": "low",
        "risk_level": "low",
        "preferred_zones": ["Maintenance", "Storage"],
    },
    "FL_10": {
        "usage_level": "low",
        "risk_level": "low",
        "preferred_zones": ["Charging", "Maintenance"],
    },
}

# Reverse map: zone -> anchors
ZONE_ANCHORS_MAP = {}
for anchor, zone in ANCHOR_ZONE_MAP.items():
    if zone not in ZONE_ANCHORS_MAP:
        ZONE_ANCHORS_MAP[zone] = []
    ZONE_ANCHORS_MAP[zone].append(anchor)

# =========================
# HELPER FUNCTIONS
# =========================
def get_shift(hour: int) -> str:
    if 6 <= hour < 14:
        return "morning"
    if 14 <= hour < 22:
        return "afternoon"
    return "night"


def generate_state_by_shift(hour: int, forklift_id: str):
    shift = get_shift(hour)
    profile = FORKLIFT_PROFILES[forklift_id]

    usage_level = profile["usage_level"]
    risk_level = profile["risk_level"]

    if shift == "morning":
        p_active = 0.50
        p_idle = 0.25
        p_available = 0.20
        p_abnormal = 0.05
        offline_prob = 0.02

    elif shift == "afternoon":
        p_active = 0.40
        p_idle = 0.30
        p_available = 0.25
        p_abnormal = 0.05
        offline_prob = 0.03

    else:
        p_active = 0.15
        p_idle = 0.15
        p_available = 0.62
        p_abnormal = 0.08
        offline_prob = 0.06

    if usage_level == "high":
        p_active += 0.10
        p_idle += 0.03
        p_available -= 0.10
        p_abnormal += 0.03
    elif usage_level == "low":
        p_active -= 0.08
        p_idle -= 0.02
        p_available += 0.08
        p_abnormal -= 0.02

    if risk_level == "high":
        p_abnormal += 0.03
        p_available -= 0.02
        offline_prob += 0.005
    elif risk_level == "medium":
        p_abnormal += 0.01

    p_active = max(p_active, 0.0)
    p_idle = max(p_idle, 0.0)
    p_available = max(p_available, 0.0)
    p_abnormal = max(p_abnormal, 0.0)

    probs = [p_active, p_idle, p_available, p_abnormal]
    total = sum(probs)
    p_active, p_idle, p_available, p_abnormal = [p / total for p in probs]

    rand = random.random()

    if rand < p_active:
        mov, occ = 1, 1
    elif rand < p_active + p_idle:
        mov, occ = 0, 1
    elif rand < p_active + p_idle + p_available:
        mov, occ = 0, 0
    else:
        mov, occ = 1, 0

    offline_rand = random.random()
    if offline_rand < offline_prob:
        visible = 0
        status = "offline"
    else:
        visible = 1
        status = "online"

    return mov, occ, visible, status


def generate_anchor_and_zone(mov: int, occ: int, forklift_id: str):
    profile = FORKLIFT_PROFILES[forklift_id]
    preferred_zones = profile["preferred_zones"]

    if mov == 1 and occ == 1:
        state_zones = ["Production", "WIP", "Storage", "Packing"]
    elif mov == 0 and occ == 1:
        state_zones = ["WIP", "Packing", "Storage"]
    elif mov == 0 and occ == 0:
        state_zones = ["Charging", "Maintenance", "Storage"]
    else:
        state_zones = ["Storage", "Packing", "WIP", "Maintenance"]

    preferred_candidates = [z for z in preferred_zones if z in state_zones]

    if preferred_candidates and random.random() < 0.75:
        zone = random.choice(preferred_candidates)
    else:
        zone = random.choice(state_zones)

    anchor = random.choice(ZONE_ANCHORS_MAP[zone])
    return anchor, zone


def apply_zone_status_correction(visible: int, status: str, zone: str):
    if status == "offline":
        return visible, status

    zone_offline_bonus = {
        "Charging": 0.010,
        "Maintenance": 0.015,
        "Storage": 0.003,
        "Packing": 0.002,
        "Production": -0.003,
        "WIP": -0.002,
    }

    correction = zone_offline_bonus.get(zone, 0.0)

    if correction > 0 and random.random() < correction:
        return 0, "offline"

    return visible, status


def generate_rssi(visible: int, zone: str):
    if visible == 0:
        return 0

    if zone in ["Production", "WIP"]:
        return random.randint(-75, -50)
    if zone in ["Storage", "Packing"]:
        return random.randint(-85, -55)
    if zone in ["Charging", "Maintenance"]:
        return random.randint(-90, -60)

    return random.randint(-90, -50)


def determine_downtime_category(
    mov: int,
    occ: int,
    visible: int,
    status: str,
    zone: str,
) -> str:
    if status == "offline" or visible == 0:
        return "signal_loss_or_offline"

    if mov == 1 and occ == 1:
        return "active_work"

    if mov == 0 and occ == 1:
        return "idle_waiting"

    if mov == 1 and occ == 0:
        return "unauthorized_operation"

    if mov == 0 and occ == 0:
        if zone in ["Charging", "Maintenance"]:
            return "parked_or_charging_candidate"
        return "available"

    return "unknown"


# =========================
# VALIDATION
# =========================
def validate_dataframe(df: pd.DataFrame) -> None:
    required_columns = [
        "timestamp",
        "date",
        "day_index",
        "forklift_id",
        "anchor",
        "zone",
        "shift",
        "rssi",
        "visible",
        "mov",
        "occ",
        "status",
        "downtime_category",
    ]

    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing columns: {missing_columns}")

    if df.empty:
        raise ValueError("Generated dataframe is empty.")

    if df[required_columns].isnull().sum().sum() > 0:
        raise ValueError("Generated dataframe contains null values.")

    valid_shifts = {"morning", "afternoon", "night"}
    valid_status = {"online", "offline"}

    if not set(df["shift"].unique()).issubset(valid_shifts):
        raise ValueError("Invalid shift values detected.")

    if not set(df["status"].unique()).issubset(valid_status):
        raise ValueError("Invalid status values detected.")

    if not df["forklift_id"].str.startswith("FL_").all():
        raise ValueError("Invalid forklift_id format detected.")

    print("Validation passed successfully.")


# =========================
# MONGODB INSERTION
# =========================
def insert_into_mongodb(df: pd.DataFrame) -> None:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[RAW_COLLECTION_NAME]

    # indexes for query performance
    collection.create_index("timestamp")
    collection.create_index("forklift_id")
    collection.create_index("day_index")

    records = []
    for row in df.to_dict("records"):
        timestamp_str = row["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
        row["_id"] = f"{row['forklift_id']}_{timestamp_str}"
        row["timestamp"] = row["timestamp"].to_pydatetime()
        records.append(row)

    if not records:
        print("No records to insert into MongoDB.")
        return

    # delete only the same day_index data, not huge _id list
    day_indexes = sorted(df["day_index"].unique().tolist())
    collection.delete_many({"day_index": {"$in": day_indexes}})
    print(f"Deleted existing records for day_index: {day_indexes}")

    # insert in batches
    batch_size = 5000
    total_inserted = 0

    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        collection.insert_many(batch)
        total_inserted += len(batch)
        print(f"Inserted {total_inserted}/{len(records)} records...")

    print(f"Inserted {total_inserted} records into MongoDB collection '{RAW_COLLECTION_NAME}'.")


# =========================
# MAIN DATA GENERATION
# =========================
records_per_forklift = (24 * 60 * 60 // INTERVAL_SECONDS) * DAYS
total_records = NUM_FORKLIFTS * records_per_forklift

print("Generating forklift dataset...")
print(f"Forklifts: {NUM_FORKLIFTS}")
print(f"Days: {DAYS}")
print(f"Interval: {INTERVAL_SECONDS} seconds")
print(f"Records per forklift: {records_per_forklift}")
print(f"Total records: {total_records}")

print("\nForklift profile summary:")
for fid, profile in FORKLIFT_PROFILES.items():
    print(fid, profile)

data = []

for forklift_num in range(1, NUM_FORKLIFTS + 1):
    forklift_id = f"FL_{forklift_num:02d}"
    current_time = START_TIME

    for _ in range(records_per_forklift):
        shift = get_shift(current_time.hour)

        mov, occ, visible, status = generate_state_by_shift(
            current_time.hour, forklift_id
        )

        anchor, zone = generate_anchor_and_zone(mov, occ, forklift_id)
        visible, status = apply_zone_status_correction(visible, status, zone)
        rssi = generate_rssi(visible, zone)

        downtime_category = determine_downtime_category(
            mov, occ, visible, status, zone
        )

        day_index = (current_time.date() - START_TIME.date()).days + 1

        record = {
            "timestamp": current_time,
            "date": current_time.date().isoformat(),
            "day_index": day_index,
            "forklift_id": forklift_id,
            "anchor": anchor,
            "zone": zone,
            "shift": shift,
            "rssi": rssi,
            "visible": visible,
            "mov": mov,
            "occ": occ,
            "status": status,
            "downtime_category": downtime_category,
        }

        data.append(record)
        current_time += timedelta(seconds=INTERVAL_SECONDS)

# Convert to DataFrame
df = pd.DataFrame(data)

# Validate before storing
validate_dataframe(df)

# Save dataset to CSV
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
output_dir = os.path.join(BASE_DIR, "output", "data")
os.makedirs(output_dir, exist_ok=True)

output_path = os.path.join(output_dir, "forklift_dataset.csv")
df.to_csv(output_path, index=False)

# Insert raw data into MongoDB
insert_into_mongodb(df)

# Print summary
print("\nData generated successfully!")
print(df.head())
print("\nDataset shape:", df.shape)

print("\nDowntime category distribution:")
print(df["downtime_category"].value_counts())

print("\nShift vs status (normalized):")
print(pd.crosstab(df["shift"], df["status"], normalize="index"))

print(f"\nSaved to: {output_path}")