"""
EdgePulse Helper Functions

Reusable helper functions for:
- Dashboard
- Executive PDF
- Future API
"""

import pandas as pd
from datetime import datetime

from utils.constants import *


# ---------------------------------------------------------------------------
# Health Summary
# ---------------------------------------------------------------------------
def get_health_summary(prediction_df):
    """
    Returns value counts of the 'Prediction' column.

    Replaces:
        summary = prediction_df["Prediction"].value_counts()
    """
    summary = prediction_df["Prediction"].value_counts()
    return summary


# ---------------------------------------------------------------------------
# Average Confidence
# ---------------------------------------------------------------------------
def get_average_confidence(prediction_df):
    """
    Returns the average confidence rounded to 2 decimal places.

    Replaces:
        prediction_df["Confidence (%)"].mean()
    """
    avg = prediction_df["Confidence (%)"].mean()
    return round(avg, 2)


# ---------------------------------------------------------------------------
# Prediction Count
# ---------------------------------------------------------------------------
def get_prediction_count(prediction_df):
    """
    Returns total number of predictions.
    Useful for PDF summary stats.
    """
    return len(prediction_df)


# ---------------------------------------------------------------------------
# Current Timestamp
# ---------------------------------------------------------------------------
def get_current_timestamp():
    """
    Returns the current timestamp formatted as:
        15 Jul 2026
        10:45 AM

    Used in:
        - Dashboard
        - PDF
        - History
    """
    now = datetime.now()
    date_part = now.strftime("%d %b %Y")
    time_part = now.strftime("%I:%M %p")
    return f"{date_part}\n{time_part}"


# ---------------------------------------------------------------------------
# Format Prediction Labels
# ---------------------------------------------------------------------------
def format_prediction_labels(label):
    """
    Adds a status emoji in front of a raw prediction label.

    Example:
        "Healthy" -> "🟢 Healthy"
    """
    label_map = {
        "Healthy": "🟢 Healthy",
        "Early_Degradation": "🟡 Early_Degradation",
        "Critical": "🟠 Critical",
        "Imminent_Failure": "🔴 Imminent_Failure",
    }
    return label_map.get(label, label)


# ---------------------------------------------------------------------------
# Alert Level
# ---------------------------------------------------------------------------
def get_alert_level(summary):
    """
    Determines the overall fleet alert level based on the health summary
    (value counts of predictions).

    Moves the large if/elif chain out of app.py so both the
    Dashboard and PDF can reuse it.

    Returns a dict with:
        title, message, color, icon
    """
    imminent_count = summary.get("Imminent_Failure", 0)
    critical_count = summary.get("Critical", 0)
    early_count = summary.get("Early_Degradation", 0)

    if imminent_count > 0:
        return {
            "title": "Imminent Failure Detected",
            "message": f"{imminent_count} machine(s) require immediate attention.",
            "color": "red",
            "icon": "🔴",
        }
    elif critical_count > 0:
        return {
            "title": "Critical Machines Detected",
            "message": f"{critical_count} machine(s) are in critical condition.",
            "color": "orange",
            "icon": "🟠",
        }
    elif early_count > 0:
        return {
            "title": "Early Degradation Detected",
            "message": f"{early_count} machine(s) showing early signs of degradation.",
            "color": "gold",
            "icon": "🟡",
        }
    else:
        return {
            "title": "Fleet Healthy",
            "message": "All machines are operating within normal parameters.",
            "color": "green",
            "icon": "🟢",
        }


# ---------------------------------------------------------------------------
# Top Critical Machines
# ---------------------------------------------------------------------------
def get_top_critical(prediction_df, top_n=10):
    """
    Returns the top N critical/high-risk machines sorted by
    Confidence (%) descending.

    Used by the PDF's "Top 10 Critical Machines" section.
    """
    critical_df = prediction_df[
        prediction_df["Prediction"].isin(["Critical", "Imminent_Failure"])
    ]
    top_critical = critical_df.sort_values(
        by="Confidence (%)", ascending=False
    ).head(top_n)
    return top_critical


# ---------------------------------------------------------------------------
# Health Counts
# ---------------------------------------------------------------------------
def get_health_counts(prediction_df):
    """
    Returns a dictionary with counts for each health stage:
        Healthy, Early_Degradation, Critical, Imminent_Failure

    Used by:
        - Health chart
        - Dashboard
        - PDF
    """
    summary = prediction_df["Prediction"].value_counts()

    counts = {
        "Healthy": int(summary.get("Healthy", 0)),
        "Early_Degradation": int(summary.get("Early_Degradation", 0)),
        "Critical": int(summary.get("Critical", 0)),
        "Imminent_Failure": int(summary.get("Imminent_Failure", 0)),
    }
    return counts