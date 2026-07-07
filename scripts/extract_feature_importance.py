import joblib
import pandas as pd

# Load trained model
model = joblib.load("models/xgb_baseline.pkl")

# Feature names
features = [
    "mean",
    "std",
    "rms",
    "max",
    "min",
    "peak_to_peak"
]

# Extract importance
importance = model.feature_importances_

# Create dataframe
importance_df = pd.DataFrame({
    "feature": features,
    "importance": importance
})

# Sort descending
importance_df = importance_df.sort_values(
    by="importance",
    ascending=False
)

# Save CSV
importance_df.to_csv(
    "models/feature_importance.csv",
    index=False
)

print("Feature importance extracted successfully!")
print(importance_df)