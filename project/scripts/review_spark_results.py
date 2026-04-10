import pandas as pd
from datetime import datetime

output_dir = "../output/spark_results"

files_to_review = {
    "category_counts": f"{output_dir}/category_counts.csv",
    "shift_counts": f"{output_dir}/shift_counts.csv",
    "zone_counts": f"{output_dir}/zone_counts.csv",
    "status_counts": f"{output_dir}/status_counts.csv",
    "avg_rssi_by_zone": f"{output_dir}/avg_rssi_by_zone.csv",
    "active_work_by_forklift": f"{output_dir}/active_work_by_forklift.csv",
    "unauthorized_by_forklift": f"{output_dir}/unauthorized_by_forklift.csv",
    "spark_sql_zone_shift_summary": f"{output_dir}/spark_sql_zone_shift_summary.csv",
    "spark_sql_offline_summary": f"{output_dir}/spark_sql_offline_summary.csv"
}

report_lines = []
report_lines.append("=== SPARK RESULTS REVIEW REPORT ===")
report_lines.append(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
report_lines.append("")

for name, path in files_to_review.items():
    df = pd.read_csv(path)

    report_lines.append(f"=== {name} ===")
    report_lines.append(f"Shape: {df.shape}")
    report_lines.append("Preview:")
    report_lines.append(df.head(10).to_string(index=False))
    report_lines.append("")

# Save review report
review_report_path = f"{output_dir}/spark_results_review_report.txt"

with open(review_report_path, "w", encoding="utf-8") as f:
    for line in report_lines:
        f.write(line + "\n")

print(f"Spark results review report saved to: {review_report_path}")