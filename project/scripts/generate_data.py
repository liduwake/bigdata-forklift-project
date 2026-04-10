import os
import random
from datetime import datetime, timedelta

import pandas as pd

# =========================
# CONFIGURATION
# =========================
NUM_FORKLIFTS = 10
#DAYS = 1
DAYS = 3
INTERVAL_SECONDS = 3
START_TIME = datetime(2026, 4, 1, 0, 0, 0)

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
    """
    Return shift name based on hour.
    """
    if 6 <= hour < 14:
        return "morning"
    if 14 <= hour < 22:
        return "afternoon"
    return "night"


def generate_state_by_shift(hour: int, forklift_id: str):
    """
    Generate mov, occ, visible, status based on:
    - shift behavior
    - forklift usage profile
    - forklift risk profile

    mov = movement (1 = moving, 0 = not moving)
    occ = occupied (1 = operator present, 0 = no operator)
    visible = sensor visibility (1 = detected, 0 = not detected)
    status = online/offline state
    """
    shift = get_shift(hour)
    profile = FORKLIFT_PROFILES[forklift_id]

    usage_level = profile["usage_level"]
    risk_level = profile["risk_level"]

    # -------------------------
    # Base probabilities by shift
    # -------------------------
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

    else:  # night
        p_active = 0.15
        p_idle = 0.15
        p_available = 0.62
        p_abnormal = 0.08
        offline_prob = 0.06

    # -------------------------
    # Usage-level adjustment
    # High-usage forklifts: more active, less available
    # Low-usage forklifts: less active, more available
    # -------------------------
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

    # -------------------------
    # Risk-level adjustment
    # Higher-risk forklifts are slightly more likely
    # to generate abnormal states
    # -------------------------
    if risk_level == "high":
        p_abnormal += 0.03
        p_available -= 0.02
        offline_prob += 0.005
    elif risk_level == "medium":
        p_abnormal += 0.01

    # Prevent negative values
    p_active = max(p_active, 0.0)
    p_idle = max(p_idle, 0.0)
    p_available = max(p_available, 0.0)
    p_abnormal = max(p_abnormal, 0.0)

    # Safety normalization
    probs = [p_active, p_idle, p_available, p_abnormal]
    total = sum(probs)
    p_active, p_idle, p_available, p_abnormal = [p / total for p in probs]

    # -------------------------
    # Generate mov and occ
    # -------------------------
    rand = random.random()

    if rand < p_active:
        mov, occ = 1, 1          # active_work
    elif rand < p_active + p_idle:
        mov, occ = 0, 1          # idle_waiting
    elif rand < p_active + p_idle + p_available:
        mov, occ = 0, 0          # available / parked
    else:
        mov, occ = 1, 0          # abnormal / unauthorized tendency

    # -------------------------
    # Generate online/offline
    # Zone correction will be applied later
    # -------------------------
    offline_rand = random.random()
    if offline_rand < offline_prob:
        visible = 0
        status = "offline"
    else:
        visible = 1
        status = "online"

    return mov, occ, visible, status


def generate_anchor_and_zone(mov: int, occ: int, forklift_id: str):
    """
    Assign anchor and zone based on:
    - forklift operational state
    - forklift preferred zones
    """
    profile = FORKLIFT_PROFILES[forklift_id]
    preferred_zones = profile["preferred_zones"]

    # State-based candidate zones
    if mov == 1 and occ == 1:
        state_zones = ["Production", "WIP", "Storage", "Packing"]
    elif mov == 0 and occ == 1:
        state_zones = ["WIP", "Packing", "Storage"]
    elif mov == 0 and occ == 0:
        state_zones = ["Charging", "Maintenance", "Storage"]
    else:  # mov == 1 and occ == 0
        state_zones = ["Storage", "Packing", "WIP", "Maintenance"]

    # Prefer the forklift's own working zones if they match state zones
    preferred_candidates = [z for z in preferred_zones if z in state_zones]

    if preferred_candidates and random.random() < 0.75:
        zone = random.choice(preferred_candidates)
    else:
        zone = random.choice(state_zones)

    anchor = random.choice(ZONE_ANCHORS_MAP[zone])
    return anchor, zone


def apply_zone_status_correction(visible: int, status: str, zone: str):
    """
    Apply small zone-based correction to offline probability.
    Shift remains the main driver. Zone is only a minor modifier.
    """
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

    # Only positive correction can turn online into offline here.
    # Negative correction is kept conceptually but does not need action
    # because the shift-based offline draw already happened.
    if correction > 0 and random.random() < correction:
        return 0, "offline"

    return visible, status


def generate_rssi(visible: int, zone: str):
    """
    Generate RSSI signal strength.
    If not visible, return 0.

    Small zone-based differences are added to make the signal pattern
    slightly more realistic.
    """
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
    """
    Classify forklift state into downtime or activity category.
    """
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

        # Apply small zone-based correction to status/visibility
        visible, status = apply_zone_status_correction(visible, status, zone)

        rssi = generate_rssi(visible, zone)

        downtime_category = determine_downtime_category(
            mov, occ, visible, status, zone
        )

        record = {
            "timestamp": current_time,
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

# Save dataset
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
output_dir = os.path.join(BASE_DIR, "output")
os.makedirs(output_dir, exist_ok=True)

output_path = os.path.join(output_dir, "data", "forklift_dataset.csv")
df.to_csv(output_path, index=False)

# Print summary
print("\nData generated successfully!")
print(df.head())
print("\nDataset shape:", df.shape)

print("\nDowntime category distribution:")
print(df["downtime_category"].value_counts())

print("\nShift vs status (normalized):")
print(pd.crosstab(df["shift"], df["status"], normalize="index"))

print(f"\nSaved to: {output_path}")