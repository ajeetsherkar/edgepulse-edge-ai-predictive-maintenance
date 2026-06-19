from fastapi import FastAPI
import joblib

app = FastAPI(
    title="EdgePulse API",
    version="1.0"
)

# Load trained model
model = joblib.load("models/xgb_baseline.pkl")


@app.get("/")
def home():
    return {
        "message": "EdgePulse API Running"
    }


@app.post("/predict")
def predict(data: dict):

    features = [[
        data["mean"],
        data["std"],
        data["rms"],
        data["max"],
        data["min"],
        data["peak_to_peak"]
    ]]

    # Prediction
    pred = int(model.predict(features)[0])

    # Confidence
    confidence = round(
        max(model.predict_proba(features)[0]) * 100,
        2
    )

    # Prediction labels
    labels = {
        0: "Healthy",
        1: "Early_Degradation",
        2: "Critical",
        3: "Failure"
    }

    # Maintenance actions
    actions = {
        "Healthy": "No Action Required",
        "Early_Degradation": "Schedule Inspection",
        "Critical": "Maintenance Within 7 Days",
        "Failure": "Immediate Shutdown Required"
    }

    return {
        "prediction": labels[pred],
        "confidence": confidence,
        "maintenance_action": actions[labels[pred]]
    }