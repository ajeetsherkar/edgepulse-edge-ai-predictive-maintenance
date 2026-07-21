import pandas as pd
import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

from reports.executive_report import generate_executive_report

# Load real prediction results (already standardized by the notebook)
results_df = pd.read_csv("data/processed/prediction_results.csv")

model_info = {
    "Model": "EdgePulse Predictive Maintenance",
    "Algorithm": "XGBoost",
    "Dataset": "NASA IMS Bearing Dataset",
    "Version": "v1.0",
    "Accuracy": "94.7%",
}

generate_executive_report(
    output_path="reports/EdgePulse_Executive_Report.pdf",
    model_info=model_info,
    results_df=results_df,
)

print("✅ Executive Report Generated Successfully!")