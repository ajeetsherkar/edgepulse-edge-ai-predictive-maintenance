import pandas as pd

# -----------------------------
# Model Performance
# -----------------------------
metrics = pd.DataFrame({
    "Metric": [
        "Accuracy",
        "Precision",
        "Recall",
        "F1 Score"
    ],
    "Value": [
        0.65,
        0.65,
        0.65,
        0.63
    ]
})

metrics.to_csv(
    "models/model_metrics.csv",
    index=False
)

# -----------------------------
# Health Distribution
# -----------------------------
dataset = pd.read_csv(
    "data/processed/labeled_dataset.csv"
)

health_distribution = (
    dataset["health_stage"]
    .value_counts()
    .reset_index()
)

health_distribution.columns = [
    "Health Stage",
    "Count"
]

health_distribution.to_csv(
    "models/health_distribution.csv",
    index=False
)

# -----------------------------
# Feature Importance
# -----------------------------
feature_importance = pd.read_csv(
    "models/feature_importance.csv"
)

feature_importance.to_csv(
    "models/dashboard_feature_importance.csv",
    index=False
)

print("Dashboard files created successfully!")