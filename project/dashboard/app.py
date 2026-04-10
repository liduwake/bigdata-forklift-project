import streamlit as st
import pandas as pd

st.set_page_config(page_title="Forklift Dashboard", layout="wide")

st.title("🚜 Forklift Big Data Dashboard")

# =========================
# LOAD DATA
# =========================
category_df = pd.read_csv("output/spark_results/category_counts.csv")
zone_df = pd.read_csv("output/spark_results/zone_counts.csv")
status_df = pd.read_csv("output/spark_results/status_counts.csv")
top_df = pd.read_csv("output/spark_results/active_work_by_forklift.csv")

# =========================
# SHOW TABLES
# =========================
st.header("📊 Top Forklifts (Active Work)")
st.dataframe(top_df)

st.header("📊 Status Distribution")
st.dataframe(status_df)

st.header("📊 Zone Distribution")
st.dataframe(zone_df)

# =========================
# SHOW CHARTS
# =========================
st.header("📈 Charts")

st.subheader("Top Forklifts")
st.bar_chart(top_df.set_index("forklift_id"))

st.subheader("Status Counts")
st.bar_chart(status_df.set_index("status"))

st.subheader("Zone Counts")
st.bar_chart(zone_df.set_index("zone"))

st.success("Dashboard loaded successfully!")