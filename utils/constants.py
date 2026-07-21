"""
EdgePulse Constants

Central location for:
- Dashboard colors
- Prediction labels
- Maintenance mappings
- UI configuration
- Theme settings
"""

# ==========================================
# Dashboard Theme Colors
# ==========================================

PRIMARY_BLUE = "#1E3A8A"
SECONDARY_BLUE = "#2563EB"

BACKGROUND = "#F8FAFC"
DIVIDER = "#CBD5E1"

SUCCESS = "#16A34A"
WARNING = "#EAB308"
ORANGE = "#F97316"
DANGER = "#DC2626"

TEXT_DARK = "#111827"
TEXT_LIGHT = "#6B7280"

# ==========================================
# Health Stage Colors
# ==========================================

HEALTH_COLORS = {
    "Healthy": "#16A34A",
    "Early_Degradation": "#EAB308",
    "Critical": "#F97316",
    "Imminent_Failure": "#DC2626",
}

color_discrete_map = HEALTH_COLORS

# ==========================================
# Prediction Labels
# ==========================================

PREDICTION_LABELS = {
    "Healthy": "🟢 Healthy",
    "Early_Degradation": "🟡 Early Degradation",
    "Critical": "🟠 Critical",
    "Imminent_Failure": "🔴 Imminent Failure",
}

# ==========================================
# Maintenance Recommendations
# ==========================================

MAINTENANCE_ACTIONS = {
    "Healthy": "No Action Required",
    "Early_Degradation": "Schedule Inspection",
    "Critical": "Maintenance Within 7 Days",
    "Imminent_Failure": "Immediate Shutdown",
}

# ==========================================
# Alert Icons
# ==========================================

STATUS_ICONS = {
    "Healthy": "🟢",
    "Early_Degradation": "🟡",
    "Critical": "🟠",
    "Imminent_Failure": "🔴",
}

# ==========================================
# Model Information
# ==========================================

MODEL_VERSION = "v1.0"

MODEL_NAME = "XGBoost"

DATASET_NAME = "NASA IMS Bearing Dataset"

MODEL_TYPE = "Multi-Class Classification"

TARGET_CLASSES = 4

DEPLOYMENT = "Edge Device Ready ⚡"

# ==========================================
# Dashboard Titles
# ==========================================

TITLES = {
    "dashboard": "📊 Executive Dashboard",
    "health": "🏭 Machine Health Distribution",
    "feature": "📈 Feature Importance",
    "confidence": "📉 Confidence Distribution",
    "maintenance": "🛠 Maintenance Action Distribution",
    "prediction": "📋 Prediction Results",
    "history": "🕒 Recent Prediction History",
    "filter": "🔍 Filter Predictions",
    "sort": "🔄 Sort Predictions",
}

# ==========================================
# Edge AI
# ==========================================

EDGE_BADGE = "⚡ Edge AI Enabled"

EDGE_DESCRIPTION = (
    "All predictions are performed locally using a lightweight "
    "XGBoost model without requiring cloud inference."
)

# ==========================================
# Chart Configuration
# ==========================================

CHART_HEIGHT = 450

CHART_WIDTH = None

PLOT_TEMPLATE = "plotly_white"

# ==========================================
# PDF Report
# ==========================================

REPORT_TITLE = "EdgePulse Executive Report"

REPORT_SUBTITLE = "Edge AI Predictive Maintenance System"

REPORT_AUTHOR = "EdgePulse"

REPORT_VERSION = "Version 1.0"

# ==========================================
# Executive PDF Theme
# ==========================================

PDF_TITLE_SIZE = 24
PDF_HEADING_SIZE = 18
PDF_TEXT_SIZE = 11
PDF_FOOTER_SIZE = 9