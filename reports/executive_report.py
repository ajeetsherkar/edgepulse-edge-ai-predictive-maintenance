from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
    KeepTogether,
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.colors import HexColor

from datetime import datetime
import os

import pandas as pd


# ============================================================
# TASK 14.1 — STANDARDIZED COLOR PALETTE
# One theme, used everywhere (headings, tables, dividers, footer).
# ============================================================

PRIMARY_COLOR = HexColor("#123E63")       # headings, table headers, divider, KPI card borders, footer line
COLOR_TABLE_BEIGE = colors.beige          # table body background
COLOR_BODY_BLACK = colors.black           # body text
COLOR_CRITICAL_RED = HexColor("#CC0000")  # imminent failure / critical KPI
COLOR_HEALTHY_GREEN = HexColor("#1E8449") # healthy KPI
COLOR_WARNING_ORANGE = HexColor("#E67E22")     # early degradation
COLOR_ORANGE_RED = HexColor("#D35400")         # critical (task 14.6)
COLOR_GREY = colors.grey


# ============================================================
# TASK 14.2 — TYPOGRAPHY HIERARCHY
# Report Title -> Title | Section Heading -> Heading2
# Subheading -> Heading3 | Body -> BodyText | Caption -> BodyText+Italic
# All headings share one font size; all body text shares one font size.
# ============================================================

def build_styles():
    base = getSampleStyleSheet()

    styles = {}

    styles["ReportTitle"] = ParagraphStyle(
        "ReportTitle",
        parent=base["Title"],
        fontName="Helvetica-Bold",
        fontSize=28,
        leading=34,
        alignment=TA_CENTER,
        textColor=PRIMARY_COLOR,
    )

    styles["Subtitle"] = ParagraphStyle(
        "Subtitle",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=16,
        alignment=TA_CENTER,
        textColor=COLOR_GREY,
    )

    styles["ReportLabel"] = ParagraphStyle(
        "ReportLabel",
        parent=base["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        alignment=TA_CENTER,
        textColor=colors.black,
    )

    styles["Tagline"] = ParagraphStyle(
        "Tagline",
        parent=base["BodyText"],
        fontName="Helvetica-Oblique",
        fontSize=12,
        alignment=TA_CENTER,
        textColor=COLOR_GREY,
    )

    # Section Heading -> Heading2, one consistent size across the whole report.
    # spaceBefore/spaceAfter kept at 0 here because gaps around headings are
    # already controlled explicitly via Spacer(1, 0.15in) / Spacer(1, 0.30in)
    # flowables (Task 14 Step 5) — adding paragraph-level spacing on top of
    # those would silently break the "one spacing rule" requirement.
    styles["SectionHeading"] = ParagraphStyle(
        "SectionHeading",
        parent=base["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=18,
        textColor=PRIMARY_COLOR,
        spaceBefore=0,
        spaceAfter=0,
    )

    # Subheading -> Heading3 (same size family, differentiated by font size
    # rather than a second blue shade, per Step 1's single-color-theme rule)
    styles["SubHeading"] = ParagraphStyle(
        "SubHeading",
        parent=base["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=13,
        textColor=PRIMARY_COLOR,
        spaceBefore=0,
        spaceAfter=0,
    )

    # Body -> BodyText, one consistent size across the whole report
    styles["Body"] = ParagraphStyle(
        "Body",
        parent=base["BodyText"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=16,
        textColor=COLOR_BODY_BLACK,
    )

    styles["InsightsBody"] = ParagraphStyle(
        "InsightsBody",
        parent=base["BodyText"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=18,
        textColor=COLOR_BODY_BLACK,
    )

    # Figure Caption -> BodyText + Italic, consistent throughout
    styles["Caption"] = ParagraphStyle(
        "Caption",
        parent=base["BodyText"],
        fontName="Helvetica-Oblique",
        fontSize=9,
        textColor=COLOR_GREY,
        alignment=TA_CENTER,
    )

    return styles


# ============================================================
# TASK 14.5 — CONSISTENT WHITE SPACE CONSTANTS
# Heading -> 0.15in -> Chart/Table -> 0.15in -> Caption -> 0.30in -> Next Section
# ============================================================

SPACE_AFTER_HEADING = 0.15 * inch
SPACE_AFTER_CONTENT = 0.15 * inch
SPACE_AFTER_SECTION = 0.30 * inch


# ============================================================
# TASK 14.6 — CONSISTENT PAGE MARGINS
# Explicit margins so the report has a clean, balanced frame on every
# page. Kept as constants so the footer line below can align to the
# same edges instead of using separate hardcoded numbers.
# ============================================================

PAGE_LEFT_MARGIN = 0.6 * inch
PAGE_RIGHT_MARGIN = 0.6 * inch
PAGE_TOP_MARGIN = 0.7 * inch
PAGE_BOTTOM_MARGIN = 0.7 * inch


# ============================================================
# TASK 14.4 — STANDARD CHART DIMENSIONS
# Every chart: 6.5in x 3.8in, centered, caption directly below.
# ============================================================

CHART_WIDTH = 6.5 * inch
CHART_HEIGHT = 3.8 * inch

# The matplotlib source figures are generated at the same aspect ratio as
# the embedded size above (6.5:3.8) so that ReportLab's fixed-size Image()
# never has to stretch/squash a chart to fit. Every chart in the report
# therefore reads at a consistent scale.
CHART_FIGSIZE = (6.5, 3.8)


def make_chart_section(image_path, caption_text, styles):
    """
    Returns a list of flowables for a chart block, following the exact
    same layout every time:
    Chart -> Spacer(0.15in) -> Caption -> Spacer(0.30in)
    """
    chart = Image(image_path, width=CHART_WIDTH, height=CHART_HEIGHT)
    chart.hAlign = "CENTER"

    caption = Paragraph(f"<i>{caption_text}</i>", styles["Caption"])

    block = [
        chart,
        Spacer(1, SPACE_AFTER_CONTENT),
        caption,
        Spacer(1, SPACE_AFTER_SECTION),
    ]
    return block


# ============================================================
# TASK 14.3 — TABLE CONSISTENCY
# Single style function reused by every table in the report so that
# header color, row height, alignment, padding, and border thickness
# are always identical.
# ============================================================

def get_standard_table_style(header_rows=1):
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, header_rows - 1), PRIMARY_COLOR),
        ("TEXTCOLOR", (0, 0), (-1, header_rows - 1), colors.white),
        ("FONTNAME", (0, 0), (-1, header_rows - 1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, header_rows - 1), 10.5),

        ("BACKGROUND", (0, header_rows), (-1, -1), COLOR_TABLE_BEIGE),
        ("FONTNAME", (0, header_rows), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, header_rows), (-1, -1), 10),

        ("GRID", (0, 0), (-1, -1), 1, COLOR_GREY),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ])


def make_standard_table(data, col_widths=None, header_rows=1):
    table = Table(data, colWidths=col_widths, hAlign="CENTER")
    table.setStyle(get_standard_table_style(header_rows=header_rows))
    return table


# ============================================================
# TASK 14.6 — DYNAMIC KPI HIGHLIGHT COLORS
# Healthy -> Green | Early Degradation -> Orange
# Critical -> Orange-Red | Imminent Failure -> Red
# ============================================================

KPI_STATUS_COLORS = {
    "Healthy": COLOR_HEALTHY_GREEN,
    "Early Degradation": COLOR_WARNING_ORANGE,
    "Critical": COLOR_ORANGE_RED,
    "Imminent Failure": COLOR_CRITICAL_RED,
}


def get_status_color(status_label, default=PRIMARY_COLOR):
    return KPI_STATUS_COLORS.get(status_label, default)


def to_hex(reportlab_color):
    """Converts a reportlab Color object to a '#rrggbb' string, usable in
    both reportlab markup and matplotlib."""
    return "#" + reportlab_color.hexval()[2:]


# ============================================================
# TASK 19 — FLEET RISK LEVEL
#
# Reuses maintenance_pct (computed a few lines above as
# (critical_count + failure_count) / total_machines * 100) rather than
# recomputing the same ratio under a new name — this file's whole design
# is "compute each figure once", and risk_percentage from the original
# spec was byte-for-byte the same formula as maintenance_pct.
# Thresholds: <5% LOW, <15% MEDIUM, <30% HIGH, >=30% CRITICAL.
# Colors reuse the existing standardized KPI palette (Task 14.1) instead
# of introducing new raw colors.* values.
# ============================================================

FLEET_RISK_THRESHOLDS = [
    (5, "LOW", COLOR_HEALTHY_GREEN),
    (15, "MEDIUM", COLOR_WARNING_ORANGE),
    (30, "HIGH", COLOR_ORANGE_RED),
]


def get_fleet_risk(risk_pct):
    for threshold, label, color in FLEET_RISK_THRESHOLDS:
        if risk_pct < threshold:
            return label, color
    return "CRITICAL", COLOR_CRITICAL_RED


# ============================================================
# TASK 16 — SINGLE SOURCE OF TRUTH FOR MAINTENANCE DATA
#
# prediction_summary and maintenance_summary are now both derived
# directly from results_df (the per-machine predictions DataFrame)
# inside generate_executive_report, instead of being authored/passed
# in separately. That was previously how the two tables could drift
# out of sync (e.g. Prediction Summary showing 350/280/210/160 while
# Maintenance Summary still showed 17/23/51/9 from stale data).
# Deriving both from the same results_df by construction makes that
# class of bug impossible.
# ============================================================

HEALTH_STAGE_ORDER = ["Healthy", "Early Degradation", "Critical", "Imminent Failure"]

HEALTH_STAGE_TO_MAINTENANCE_ACTION = {
    "Healthy": "Monitor",
    "Early Degradation": "Schedule Inspection",
    "Critical": "Maintain Within 7 Days",
    "Imminent Failure": "Immediate Shutdown",
}

# Maintenance actions, kept in the same order as HEALTH_STAGE_ORDER so the
# Maintenance Summary table always lines up with the Prediction Summary
# table row-for-row.
MAINTENANCE_ORDER = [
    HEALTH_STAGE_TO_MAINTENANCE_ACTION[stage] for stage in HEALTH_STAGE_ORDER
]

# RECOMMENDATION_MAPPING is the prediction -> action lookup used to build
# the Maintenance Recommendations table. It's an alias for
# HEALTH_STAGE_TO_MAINTENANCE_ACTION rather than a second dict with the
# same contents — this file's whole design is "one source of truth per
# fact", and prediction -> action is already that fact.
RECOMMENDATION_MAPPING = HEALTH_STAGE_TO_MAINTENANCE_ACTION

# Priority level shown alongside each recommendation, one severity step
# per health stage. Uses the same HEALTH_STAGE_ORDER progression as
# everywhere else in the file rather than a new ranking scheme.
PRIORITY_MAPPING = {
    "Healthy": "Low",
    "Early Degradation": "Medium",
    "Critical": "High",
    "Imminent Failure": "Critical",
}


# ============================================================
# TASK 17 (expanded) — RESULTS_DF / MODEL_INFO / CHART INPUT VALIDATION
#
# validate_results_df originally only checked that the three required
# columns existed. It's expanded here to also cover the other ways a
# caller can hand generate_executive_report a bad input — None/empty
# DataFrames, wrong types, out-of-range confidence values, and
# prediction/maintenance labels the rest of this file doesn't know how
# to render — so that a bad input fails once, loudly, and clearly at
# the top of the function instead of surfacing as a confusing KeyError,
# IndexError, or silently-wrong chart somewhere in the middle of report
# generation.
#
# VALID_PREDICTIONS / VALID_MAINTENANCE deliberately reuse
# HEALTH_STAGE_ORDER / MAINTENANCE_ORDER (as sets) rather than
# hardcoding a second list of the same four labels — this file's whole
# design is "one source of truth per fact", and the set of valid
# prediction/maintenance labels is already that fact, defined above.
# ============================================================

VALID_PREDICTIONS = set(HEALTH_STAGE_ORDER)
VALID_MAINTENANCE = set(MAINTENANCE_ORDER)


def validate_results_df(results_df):
    """Validates the prediction results DataFrame passed to
    generate_executive_report. Raises TypeError for a wrong input type,
    and ValueError for anything else that's structurally or semantically
    wrong (missing, empty, missing columns, invalid confidence values,
    or unrecognized prediction/maintenance labels)."""

    if not isinstance(results_df, pd.DataFrame):
        raise TypeError("results_df must be a pandas DataFrame.")

    if results_df is None:
        raise ValueError("results_df cannot be None.")

    if results_df.empty:
        raise ValueError("results_df is empty.")

    required_columns = [
        "Prediction",
        "Maintenance",
        "Confidence (%)",
    ]

    missing = [
        col
        for col in required_columns
        if col not in results_df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {', '.join(missing)}"
        )

    confidence = results_df["Confidence (%)"]

    if confidence.isnull().any():
        raise ValueError("Confidence (%) contains missing values.")

    if not confidence.between(0, 100).all():
        raise ValueError("Confidence (%) must be between 0 and 100.")

    unexpected_predictions = (
        set(results_df["Prediction"].unique()) - VALID_PREDICTIONS
    )
    if unexpected_predictions:
        raise ValueError(
            f"Unexpected prediction labels: {sorted(unexpected_predictions)}"
        )

    unexpected_maintenance = (
        set(results_df["Maintenance"].unique()) - VALID_MAINTENANCE
    )
    if unexpected_maintenance:
        raise ValueError(
            f"Unexpected maintenance labels: {sorted(unexpected_maintenance)}"
        )


def validate_model_info(model_info):
    """Validates the model_info dict. Several sections of the report
    (cover page, Executive Summary, KPI cards, Model Information,
    Conclusion) read model_info's keys directly (model_info["Model"],
    ["Algorithm"], ["Dataset"], ["Version"], ["Accuracy"]) with no
    fallback, so every key any of those sections needs is checked here,
    up front. This used to check only "Accuracy", which let a caller
    hand in a dict missing "Model"/"Algorithm"/"Dataset"/"Version" and
    have it explode as a bare, confusing KeyError deep inside
    _build_executive_report (e.g. while building the cover table or the
    Model Information table) instead of failing clearly here."""

    if not isinstance(model_info, dict):
        raise TypeError("model_info must be a dictionary.")

    if model_info is None:
        raise ValueError("model_info cannot be None.")

    required_keys = ["Model", "Algorithm", "Dataset", "Version", "Accuracy"]
    missing = [key for key in required_keys if key not in model_info]
    if missing:
        raise ValueError(
            f"model_info is missing required keys: {', '.join(missing)}"
        )


def validate_feature_importances(feature_importances):
    """Validates a feature-importance DataFrame, if one was supplied
    directly (as opposed to being read from a CSV path via
    load_feature_importance). Optional — only checked when not None, since
    generate_executive_report's default path loads feature importance from
    a CSV rather than receiving a DataFrame."""

    if feature_importances is None:
        return

    if feature_importances.empty:
        raise ValueError("feature_importances is empty.")

    required = ["Feature", "Importance"]
    missing = [c for c in required if c not in feature_importances.columns]

    if missing:
        raise ValueError(f"feature_importances missing columns: {missing}")


def validate_chart_files(chart_paths):
    """Validates that any chart image paths supplied already exist on
    disk. For chart *image* inputs only — this module doesn't generate
    input images, only output PNGs, so a caller-supplied chart image path
    should fail clearly here rather than blow up later wherever it's
    used. Not used for the feature-importance CSV input; see
    validate_csv_file() for that (Task 26) — a CSV isn't a chart, so it
    gets its own, more accurately-named check."""

    for chart in chart_paths or []:
        if not os.path.exists(chart):
            raise FileNotFoundError(f"Chart not found: {chart}")


# ============================================================
# TASK 26 — DEDICATED CSV INPUT VALIDATION
#
# validate_chart_files() was previously reused to check the
# feature-importance CSV input, but that function's name and docstring
# are about chart *images* — reusing it for a CSV was a category
# mismatch that made the validation harder to read at the call site.
# validate_csv_file() exists solely to check that a CSV input path
# exists, with an error message that says "CSV" rather than "Chart".
# ============================================================

def validate_csv_file(csv_path):
    """Validates that a required CSV input file exists on disk. Used for
    the feature-importance CSV path (chart_paths["feature_importance_csv"]),
    which — unlike the four chart PNG paths this module generates itself
    — is external input data this module doesn't produce, so a
    missing/mistyped path here should fail clearly and by name ("CSV",
    not "Chart") rather than surface later as a less informative error
    from inside pandas.read_csv."""

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Feature importance CSV not found: {csv_path}")


# ============================================================
# TASK 24 — LABEL NORMALIZATION (underscore/whitespace/case drift)
#
# The model pipeline emits Prediction/Maintenance labels with
# underscores instead of spaces (e.g. "Early_Degradation",
# "Imminent_Failure"), which fails validate_results_df() since
# VALID_PREDICTIONS/VALID_MAINTENANCE are defined with spaces
# (HEALTH_STAGE_ORDER / MAINTENANCE_ORDER). normalize_label_series()
# is applied to both columns immediately after the rename and before
# validation, so the single source-of-truth label sets never need to
# change — the raw data is normalized to match them instead of the
# other way around. Stripping surrounding whitespace and title-casing
# is included defensively for the same class of drift (extra spaces,
# inconsistent casing from upstream); if a genuinely unrecognized label
# is produced, validate_results_df() still raises clearly rather than
# silently coercing it into something wrong.
# ============================================================

def normalize_label_series(series):
    """Normalizes a Prediction/Maintenance label Series so that
    underscore-separated, extra-whitespace, or inconsistently-cased
    variants (e.g. 'Early_Degradation', ' critical ', 'IMMEDIATE
    SHUTDOWN') match the space-separated, title-cased labels defined in
    HEALTH_STAGE_ORDER / MAINTENANCE_ORDER. Anything that still doesn't
    match a known label after this is left as-is, so
    validate_results_df() catches it and raises with a clear message."""
    return (
        series.astype(str)
        .str.strip()
        .str.replace("_", " ", regex=False)
        .str.title()
    )


# ============================================================
# TASK 25 — MAINTENANCE LABEL SYNONYMS
#
# Unlike the underscore/whitespace/case drift handled by
# normalize_label_series(), the upstream dataset also produces genuine
# synonyms for two Maintenance actions — different words for the same
# concept, not just different formatting of the same words:
#   "No Action Required"          -> "Monitor"
#   "Maintenance Within 7 Days"   -> "Maintain Within 7 Days"
# No amount of case/whitespace/underscore normalization can bridge that
# gap, so it's an explicit lookup instead. Kept as its own named mapping
# (rather than inline in generate_executive_report) so it's visible and
# editable in one place if the upstream pipeline introduces another
# synonym later. Applied AFTER normalize_label_series() so the lookup
# only has to handle the canonical title-cased spelling of each synonym,
# not every possible casing/whitespace variant of it too.
# ============================================================

MAINTENANCE_LABEL_SYNONYMS = {
    "No Action Required": "Monitor",
    "Maintenance Within 7 Days": "Maintain Within 7 Days",
}


def apply_maintenance_synonyms(series):
    """Maps known Maintenance-label synonyms (MAINTENANCE_LABEL_SYNONYMS)
    onto their canonical MAINTENANCE_ORDER spelling. Labels not present in
    the mapping pass through unchanged, so a genuinely unrecognized label
    still reaches validate_results_df() and raises there instead of being
    silently coerced."""
    return series.replace(MAINTENANCE_LABEL_SYNONYMS)


# ============================================================
# TASK 18 — CHARTS GENERATED FROM DATA, NOT LOADED AS STATIC FILES
#
# The PDF previously embedded pre-existing PNGs on disk, so changing the
# input DataFrames had no effect unless a separate chart script was
# rerun first. Every chart below is now regenerated directly from
# results_df (or, for feature importance, from feature_importance.csv)
# on every report build, so none of them can ever go stale relative to
# the data actually described in the report. There is no manual "update
# the PNG" workflow left anywhere — generate_executive_report is the
# only thing that ever writes these files.
# ============================================================

def _render_bar_chart(labels, values, bar_colors, output_path, ylabel="Machine Count", title=None, xtick_rotation=0):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=CHART_FIGSIZE)
    ax.bar(labels, values, color=bar_colors)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    # Task 27 — rotate x-axis labels when they're long enough to crowd
    # each other at this chart's fixed width (e.g. "Maintain Within 7
    # Days" / "Immediate Shutdown"). Right-aligning the rotated labels
    # (ha="right") keeps each one anchored under its own bar instead of
    # drifting sideways.
    if xtick_rotation:
        plt.setp(ax.get_xticklabels(), rotation=xtick_rotation, ha="right")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def generate_health_distribution_chart(prediction_summary, output_path):
    """Regenerates health_distribution.png directly from prediction_summary,
    in the fixed Healthy -> Early Degradation -> Critical -> Imminent
    Failure order, colored to match the KPI cards and recommendations
    table. The chart title reports the total machine count directly from
    prediction_summary, so it's never a hardcoded figure that could drift
    from the data actually plotted."""
    counts_by_stage = prediction_summary.set_index("Health Stage")["Count"]
    ordered_counts = [int(counts_by_stage.get(stage, 0)) for stage in HEALTH_STAGE_ORDER]
    bar_colors = [to_hex(get_status_color(stage)) for stage in HEALTH_STAGE_ORDER]
    total_in_chart = sum(ordered_counts)
    chart_title = f"Machine Health Distribution ({total_in_chart} Machines)"
    _render_bar_chart(
        HEALTH_STAGE_ORDER, ordered_counts, bar_colors, output_path, title=chart_title
    )


def generate_maintenance_distribution_chart(maintenance_summary, output_path):
    """Regenerates maintenance_distribution.png directly from
    maintenance_summary, in the fixed Monitor -> Schedule Inspection ->
    Maintain Within 7 Days -> Immediate Shutdown order (MAINTENANCE_ORDER),
    colored to match the corresponding health stage. Built exactly like
    generate_health_distribution_chart, just keyed off results_df["Maintenance"]
    instead of results_df["Prediction"]. Labels are rotated (Task 27) since
    "Maintain Within 7 Days" and "Immediate Shutdown" are long enough to
    overlap at this chart's fixed width when printed horizontally."""
    counts_by_action = maintenance_summary.set_index("Maintenance")["Count"]
    ordered_counts = [int(counts_by_action.get(action, 0)) for action in MAINTENANCE_ORDER]
    bar_colors = [
        to_hex(get_status_color(stage)) for stage in HEALTH_STAGE_ORDER
    ]
    total_in_chart = sum(ordered_counts)
    chart_title = f"Maintenance Action Distribution ({total_in_chart} Machines)"
    _render_bar_chart(
        MAINTENANCE_ORDER, ordered_counts, bar_colors, output_path,
        title=chart_title, xtick_rotation=20,
    )


def generate_confidence_distribution_chart(confidence_scores, output_path):
    """Builds a confidence histogram from raw per-machine confidence scores
    (0-1 or 0-100), e.g. results_df["Confidence (%)"]. Called on every
    report build, so the chart always reflects the results_df passed to
    generate_executive_report rather than a leftover PNG on disk."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    scores = [s * 100 if s <= 1 else s for s in confidence_scores]

    fig, ax = plt.subplots(figsize=CHART_FIGSIZE)
    ax.hist(scores, bins=20, color=to_hex(PRIMARY_COLOR), edgecolor="white")
    ax.set_xlabel("Prediction Confidence (%)")
    ax.set_ylabel("Machine Count")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def load_feature_importance(csv_path):
    """Reads a feature-importance CSV and returns a DataFrame with
    normalized 'feature' and 'importance' columns, sorted by importance
    descending (most important first). Column names are matched
    case-insensitively against 'feature'/'importance'; falls back to the
    first two columns if those names aren't found. Shared by
    generate_feature_importance_chart and the Feature Importance summary
    section in generate_executive_report, so both read the CSV the same
    way and can never disagree about which feature is "top"."""

    fi_df = pd.read_csv(csv_path)

    columns_by_lower_name = {c.lower(): c for c in fi_df.columns}
    feature_col = columns_by_lower_name.get("feature", fi_df.columns[0])
    importance_col = columns_by_lower_name.get("importance", fi_df.columns[1])

    fi_df = fi_df[[feature_col, importance_col]].dropna()
    fi_df.columns = ["feature", "importance"]
    fi_df = fi_df.sort_values(by="importance", ascending=False).reset_index(drop=True)
    return fi_df


# ============================================================
# TASK 22 — FEATURE IMPORTANCE INTERPRETATION
# Maps a feature name to a plain-language explanation for the Feature
# Importance summary table/insight. .get() with a generic fallback below
# means an unrecognized feature name (e.g. the model is retrained on a
# different feature set) degrades gracefully instead of raising.
# ============================================================

FEATURE_EXPLANATIONS = {
    "rms": "High RMS values indicate increased vibration severity and possible bearing degradation.",
    "mean": "Mean vibration reflects the overall operating condition of the machine.",
    "std": "High standard deviation indicates unstable vibration behaviour.",
    "max": "Peak vibration values may indicate impact events or mechanical shocks.",
    "min": "Minimum vibration helps identify baseline operating behaviour.",
    "peak_to_peak": "Peak-to-peak vibration captures overall signal amplitude and fault intensity.",
}


def generate_feature_importance_chart(csv_path, output_path, top_n=10):
    """Reads feature importances via load_feature_importance() and
    regenerates feature_importance.png from it on every report build, so
    the chart can never go stale relative to the CSV's contents (no more
    editing/replacing the PNG by hand). The top feature's bar is colored
    differently from the rest so it stands out immediately (Task 22 Step 8).
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fi_df = load_feature_importance(csv_path).head(top_n)
    # barh draws bottom-to-top; reverse so the top feature (first row,
    # descending order) ends up drawn at the top of the chart.
    fi_df = fi_df.iloc[::-1]

    names = fi_df["feature"].tolist()
    values = fi_df["importance"].tolist()

    bar_colors = [to_hex(PRIMARY_COLOR)] * len(names)
    if bar_colors:
        bar_colors[-1] = to_hex(COLOR_WARNING_ORANGE)  # top feature, drawn last (top of chart)

    fig, ax = plt.subplots(figsize=CHART_FIGSIZE)
    ax.barh(names, values, color=bar_colors)
    ax.set_xlabel("Importance")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def create_kpi_card(title, value, value_color):
    card = Table([
        [
            Paragraph(
                f"""
                <para align="center">
                <font size="11"><b>{title}</b></font>
                <br/><br/>
                <font size="24" color="{value_color}">
                <b>{value}</b>
                </font>
                </para>
                """,
                getSampleStyleSheet()["BodyText"],
            )
        ]
    ], colWidths=3.0 * inch, rowHeights=1.25 * inch)

    card.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 2, PRIMARY_COLOR),
        ("BACKGROUND", (0, 0), (-1, -1), HexColor("#F8FAFC")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ]))

    return card


def generate_executive_report(
    output_path,
    model_info,
    results_df,
    chart_paths=None,
    feature_importances=None,
):
    """
    Generates the Executive PDF Report with standardized, consulting-grade
    styling (Task 14): consistent colors, typography hierarchy, table
    formatting, image alignment, white space, and dynamic KPI colors.

    results_df: per-machine predictions DataFrame with a "Prediction"
    column (values drawn from HEALTH_STAGE_ORDER), a "Maintenance" column
    (values drawn from MAINTENANCE_ORDER), and a "Confidence (%)" column.
    The Prediction Summary and Maintenance Summary tables, the KPI cards,
    and the health/maintenance/confidence distribution charts are all
    derived directly from this single DataFrame on every call, so they
    can never disagree with each other or go stale.

    Prediction/Maintenance values are normalized (underscore -> space,
    trimmed, title-cased) immediately after the column rename and before
    validation, so upstream label formatting quirks (e.g.
    "Early_Degradation") don't need a schema change here — see
    normalize_label_series() (Task 24). Maintenance values are then also
    passed through MAINTENANCE_LABEL_SYNONYMS (Task 25) to resolve true
    synonyms like "No Action Required" -> "Monitor" that formatting
    normalization alone can't bridge.

    model_info: dict describing the trained model, required to contain
    "Model", "Algorithm", "Dataset", "Version", and "Accuracy" — every
    key any section of the report (cover page, Model Information table,
    KPI cards, Executive Summary, Conclusion) reads directly. Validated
    up front by validate_model_info() so a missing key fails clearly
    here instead of as a KeyError mid-build.

    feature_importances: optional pre-loaded feature-importance DataFrame
    with "Feature"/"Importance" columns. Validated if supplied, but not
    otherwise used by default — the report reads feature importance from
    chart_paths["feature_importance_csv"] via load_feature_importance().

    chart_paths: dict of output/input paths for the charts, with defaults
    under reports/charts/. Recognized keys:
      - "health_distribution": output PNG, regenerated from results_df["Prediction"]
      - "maintenance_distribution": output PNG, regenerated from results_df["Maintenance"]
      - "confidence_distribution": output PNG, regenerated from results_df["Confidence (%)"]
      - "feature_importance": output PNG, regenerated from the CSV below
      - "feature_importance_csv": input CSV of {feature, importance} rows
    Any key not supplied falls back to its default reports/charts/ location.
    Every chart is regenerated on every call — there is no manual "update
    the PNG" step; the report is always the only thing that writes these
    files.

    Raises TypeError/ValueError/FileNotFoundError if the inputs above fail
    validation, and RuntimeError (wrapping the original exception) if PDF
    generation itself fails after validation passes.
    """

    # ==========================
    # Input validation, in the order: results_df -> model_info ->
    # feature_importances (if provided) -> chart input files (if
    # provided). Each of these fails fast with a clear, specific message
    # before any report-building work (chart generation, PDF assembly)
    # begins.
    # ==========================
    results_df = results_df.rename(columns={
        "prediction": "Prediction",
        "confidence": "Confidence (%)",
        "maintenance_action": "Maintenance"
    })

    # TASK 24 — normalize label formatting (underscores/whitespace/case)
    # BEFORE validation, so validate_results_df() and everything
    # downstream (prediction_summary, maintenance_summary, the
    # Prediction<->Maintenance consistency asserts, chart generation) all
    # see labels that already match HEALTH_STAGE_ORDER / MAINTENANCE_ORDER
    # exactly. Doing this after validation, or only in some code paths,
    # would let inconsistent labels slip past the fail-fast check here
    # and surface later as a confusing AssertionError instead.
    results_df["Prediction"] = normalize_label_series(results_df["Prediction"])
    results_df["Maintenance"] = normalize_label_series(results_df["Maintenance"])

    # TASK 25 — apply Maintenance synonym mapping AFTER normalization
    # (case/whitespace/underscore) but still BEFORE validation, so
    # genuine synonyms like "No Action Required" -> "Monitor" resolve to
    # the canonical MAINTENANCE_ORDER spelling before validate_results_df()
    # checks it, exactly like the Prediction/Maintenance normalization
    # above.
    results_df["Maintenance"] = apply_maintenance_synonyms(results_df["Maintenance"])

    validate_results_df(results_df)
    validate_model_info(model_info)
    validate_feature_importances(feature_importances)

    default_chart_paths = {
        "health_distribution": "reports/charts/health_distribution.png",
        "maintenance_distribution": "reports/charts/maintenance_distribution.png",
        "confidence_distribution": "reports/charts/confidence_distribution.png",
        "feature_importance": "reports/charts/feature_importance.png",
        "feature_importance_csv": "models/feature_importance.csv",
    }
    chart_paths = {**default_chart_paths, **(chart_paths or {})}

    # Only the feature-importance CSV is an input this module doesn't
    # itself produce (the four PNG paths above are outputs, generated a
    # few lines down) — so that's the one path checked for existence
    # here. It's a CSV, not a chart image, so it gets its own validator
    # (Task 26) rather than being run through validate_chart_files(). A
    # missing/mistyped path fails clearly now rather than surfacing as a
    # confusing error from inside pandas.read_csv later.
    validate_csv_file(chart_paths["feature_importance_csv"])

    # Guard against a prediction label showing up in the data that has no
    # corresponding entry in RECOMMENDATION_MAPPING (e.g. the model is
    # retrained with a new health stage). Failing loudly here beats
    # silently omitting that class's row from the Maintenance
    # Recommendations table further down.
    prediction_classes = set(results_df["Prediction"].unique())
    missing_recommendations = prediction_classes - set(RECOMMENDATION_MAPPING.keys())
    if missing_recommendations:
        raise ValueError(
            f"No maintenance recommendation defined for: {sorted(missing_recommendations)}"
        )

    print("Entering _build_executive_report")
    try:
        pdf_path = _build_executive_report(
            output_path=output_path,
            model_info=model_info,
            results_df=results_df,
            chart_paths=chart_paths,
        )

        print("Returned from _build_executive_report:", pdf_path)

        return pdf_path
    except Exception as e:
        raise RuntimeError(f"Failed to generate executive report: {e}") from e


def _build_executive_report(output_path, model_info, results_df, chart_paths):
    """Does the actual report-building work (KPI computation, chart
    generation, PDF assembly). Split out from generate_executive_report so
    that all input validation happens first and unconditionally, while
    this function's own failures are the ones wrapped into a single clear
    RuntimeError by the caller's try/except."""

    # ==========================
    # TASK 2 — SINGLE SOURCE FOR EVERY KPI IN THE REPORT
    #
    # Every count, percentage, and average shown anywhere in the report
    # (KPI cards, insights, recommendations, conclusion, chart titles) is
    # computed once, here, directly from results_df/model_info. Nothing
    # downstream is allowed to hardcode a number — if the data changes,
    # every section that references these variables changes with it.
    # ==========================

    total_machines = len(results_df)

    healthy_count = int((results_df["Prediction"] == "Healthy").sum())
    early_count = int((results_df["Prediction"] == "Early Degradation").sum())
    critical_count = int((results_df["Prediction"] == "Critical").sum())
    failure_count = int((results_df["Prediction"] == "Imminent Failure").sum())

    confidence = results_df["Confidence (%)"]
    avg_confidence = confidence.mean()
    min_confidence = confidence.min()
    max_confidence = confidence.max()
    std_confidence = confidence.std()

    healthy_pct = (healthy_count / total_machines * 100) if total_machines else 0
    critical_pct = (critical_count / total_machines * 100) if total_machines else 0
    failure_pct = (failure_count / total_machines * 100) if total_machines else 0

    inspection_count = int((results_df["Maintenance"] == "Schedule Inspection").sum())
    inspection_pct = (inspection_count / total_machines * 100) if total_machines else 0

    # Combined near-term maintenance workload (Critical + Imminent Failure),
    # used both in Operational Insights and the Conclusion's risk framing.
    maintenance_required = critical_count + failure_count
    maintenance_pct = (maintenance_required / total_machines * 100) if total_machines else 0

    # TASK 19 — Fleet Risk Level, derived from maintenance_pct above (same
    # (critical + failure) / total ratio) rather than a second computation.
    fleet_risk, risk_color = get_fleet_risk(maintenance_pct)

    def format_accuracy(info):
        """Formats model accuracy from model_info instead of hardcoding it.
        Accepts a percentage string ("94.7%"), a 0-100 number (94.7), or a
        0-1 fraction (0.947). Falls back to 'N/A' if not supplied, rather
        than displaying a made-up figure. Moved up here (Task 20) so both
        the Executive Summary and the KPI cards read the same formatted
        value instead of formatting accuracy twice."""
        value = info.get("Accuracy")
        if value is None:
            return "N/A"
        if isinstance(value, str):
            return value
        value = float(value)
        if value <= 1:
            value *= 100
        return f"{value:.1f}%"

    accuracy_display = format_accuracy(model_info)

    if avg_confidence >= 95:
        confidence_level = "Excellent"
    elif avg_confidence >= 90:
        confidence_level = "High"
    elif avg_confidence >= 80:
        confidence_level = "Moderate"
    else:
        confidence_level = "Low"

    if failure_count > 0:
        priority = "Immediate shutdown required for high-risk machines."
    elif critical_count > 0:
        priority = "Prioritize corrective maintenance."
    else:
        priority = "Fleet operating within acceptable limits."

    prediction_summary = (
        results_df["Prediction"]
        .value_counts()
        .reindex(HEALTH_STAGE_ORDER, fill_value=0)
        .rename_axis("Health Stage")
        .reset_index(name="Count")
    )

    maintenance_summary = (
        results_df["Maintenance"]
        .value_counts()
        .reindex(MAINTENANCE_ORDER, fill_value=0)
        .rename_axis("Maintenance")
        .reset_index(name="Count")
    )

    # ==========================
    # Consistency check: each health stage's Prediction count must match
    # its corresponding Maintenance action's count. If these ever
    # disagree, the two source columns in results_df have drifted apart
    # (e.g. a row's Maintenance action doesn't match its Prediction), and
    # that's a data problem that should fail loudly here rather than
    # produce a report where the two summary tables silently disagree.
    # ==========================
    assert (
        (results_df["Prediction"] == "Healthy").sum()
        ==
        (results_df["Maintenance"] == "Monitor").sum()
    )

    assert (
        (results_df["Prediction"] == "Early Degradation").sum()
        ==
        (results_df["Maintenance"] == "Schedule Inspection").sum()
    )

    assert (
        (results_df["Prediction"] == "Critical").sum()
        ==
        (results_df["Maintenance"] == "Maintain Within 7 Days").sum()
    )

    assert (
        (results_df["Prediction"] == "Imminent Failure").sum()
        ==
        (results_df["Maintenance"] == "Immediate Shutdown").sum()
    )

    # Every chart is fully derivable from results_df (or, for feature
    # importance, from the CSV file at chart_paths["feature_importance_csv"]),
    # so all four are regenerated unconditionally on every build. None of
    # them can ever be a stale image left over from a previous dataset,
    # and there's no separate manual step required to keep them current.
    generate_health_distribution_chart(
        prediction_summary, chart_paths["health_distribution"]
    )
    generate_maintenance_distribution_chart(
        maintenance_summary, chart_paths["maintenance_distribution"]
    )
    generate_confidence_distribution_chart(
        confidence, chart_paths["confidence_distribution"]
    )
    generate_feature_importance_chart(
        chart_paths["feature_importance_csv"], chart_paths["feature_importance"]
    )

    doc = SimpleDocTemplate(
        output_path,
        rightMargin=PAGE_RIGHT_MARGIN,
        leftMargin=PAGE_LEFT_MARGIN,
        topMargin=PAGE_TOP_MARGIN,
        bottomMargin=PAGE_BOTTOM_MARGIN,
    )
    styles = build_styles()

    elements = []

    # ==========================
    # Report Title / Cover
    # ==========================

    generated_time = datetime.now().strftime("%d %B %Y, %I:%M %p")

    title = Paragraph("EdgePulse", styles["ReportTitle"])
    subtitle = Paragraph("Edge-AI Predictive Maintenance System", styles["Subtitle"])
    report_label = Paragraph("Executive Report", styles["ReportLabel"])

    divider = Table([[""]], colWidths=[6.5 * inch], rowHeights=[2])
    divider.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PRIMARY_COLOR),
    ]))

    cover_table = Table([
        ["Model", model_info["Algorithm"]],
        ["Dataset", model_info["Dataset"]],
        ["Version", model_info["Version"]],
        ["Generated", generated_time],
    ], colWidths=[1.7 * inch, 4.3 * inch])

    cover_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), PRIMARY_COLOR),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.white),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("BACKGROUND", (1, 0), (1, -1), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.5, COLOR_GREY),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]))

    tagline = Paragraph(
        "AI-powered industrial health monitoring and predictive maintenance.",
        styles["Tagline"],
    )

    # Intentional exception to the 0.15in/0.30in spacing rule: this is pure
    # top whitespace to vertically balance the cover block, not a gap
    # between a heading and its content.
    COVER_TOP_SPACE = 0.6 * inch

    elements.append(Spacer(1, COVER_TOP_SPACE))
    elements.append(title)
    elements.append(subtitle)
    elements.append(Spacer(1, SPACE_AFTER_SECTION))
    elements.append(report_label)
    elements.append(Spacer(1, SPACE_AFTER_SECTION))
    elements.append(divider)
    elements.append(Spacer(1, SPACE_AFTER_SECTION))
    elements.append(cover_table)
    elements.append(Spacer(1, SPACE_AFTER_SECTION))
    elements.append(tagline)
    elements.append(Spacer(1, SPACE_AFTER_SECTION))

    # ==========================
    # TASK 20 — EXECUTIVE SUMMARY
    # Heading + compact metrics table + short narrative + highlight
    # bullets, placed right after the cover page so it reads as a
    # one-page overview before the KPI cards / detailed sections.
    # Uses make_standard_table() (Task 14.3) and accuracy_display
    # (computed once above) rather than a new table style or a second
    # accuracy-formatting pass.
    # ==========================

    elements.append(Paragraph("Executive Summary", styles["SectionHeading"]))
    elements.append(Spacer(1, SPACE_AFTER_HEADING))

    summary_data = [
        ["Metric", "Value"],
        ["Machines Analysed", str(total_machines)],
        ["Model Accuracy", accuracy_display],
        ["Average Confidence", f"{avg_confidence:.1f}%"],
        ["Overall Fleet Risk", fleet_risk],
        ["Critical Machines", str(critical_count)],
        ["Immediate Shutdown", str(failure_count)],
    ]

    elements.append(
        make_standard_table(summary_data, col_widths=[2.5 * inch, 4.0 * inch])
    )
    elements.append(Spacer(1, SPACE_AFTER_CONTENT))

    # Key figures are bolded inline (rather than the whole paragraph) so
    # they stand out to a reader scanning the summary without the
    # narrative reading like a wall of bold text.
    summary_text = (
        f"The EdgePulse system analysed <b>{total_machines}</b> rotating machinery "
        f"samples using an XGBoost-based predictive maintenance model. The "
        f"model achieved an accuracy of <b>{accuracy_display}</b> with an average "
        f"prediction confidence of <b>{avg_confidence:.1f}%</b>. Based on the current "
        f"analysis, the fleet risk level is classified as <b>{fleet_risk}</b>. "
        f"Preventive maintenance should prioritise critical and imminent "
        f"failure machines to minimise downtime and operational costs."
    )

    elements.append(Paragraph(summary_text, styles["Body"]))
    elements.append(Spacer(1, SPACE_AFTER_CONTENT))

    highlights = [
        f"Analysed <b>{total_machines}</b> machine records.",
        f"Detected <b>{critical_count}</b> critical assets.",
        f"<b>{failure_count}</b> machines require immediate shutdown.",
        f"Average prediction confidence: <b>{avg_confidence:.1f}%</b>.",
        f"Overall fleet risk: <b>{fleet_risk}</b>.",
    ]

    for item in highlights:
        elements.append(Paragraph(f"&bull; {item}", styles["InsightsBody"]))
        elements.append(Spacer(1, 0.08 * inch))

    elements.append(Spacer(1, SPACE_AFTER_HEADING))

    # ==========================
    # Model Information
    #
    # Relocated here, below the Executive Summary highlights, instead of
    # its previous spot right after the Health Distribution chart. In its
    # old position this table landed alone at the top of its own page
    # (the KPI cards + Health Distribution chart above it already filled
    # the prior page), leaving most of that page blank. Placing it here
    # lets it share the Executive Summary page instead of forcing a
    # near-empty page of its own.
    # ==========================

    elements.append(Paragraph("Model Information", styles["SectionHeading"]))
    elements.append(Spacer(1, SPACE_AFTER_HEADING))

    model_table_data = [
        ["Property", "Value"],
        ["Model", model_info["Model"]],
        ["Algorithm", model_info["Algorithm"]],
        ["Dataset", model_info["Dataset"]],
        ["Version", model_info["Version"]],
    ]

    elements.append(make_standard_table(model_table_data))
    elements.append(Spacer(1, SPACE_AFTER_SECTION))

    # PageBreak() removed here — it was forcing KPI Cards onto a fresh
    # page even when room remained on this one. KPI Cards now flow
    # naturally, using whatever space is left before moving on.

    # ==========================
    # KPI Cards (Task 14.6 — dynamic highlight colors)
    # ==========================

    # total_machines, healthy_count, early_count, critical_count,
    # failure_count, avg_confidence, healthy_pct, critical_pct,
    # failure_pct, and fleet_risk/risk_color were all computed once,
    # right after validation, so every number below is guaranteed to
    # come from results_df / model_info rather than a hardcoded literal.

    accuracy = create_kpi_card(
        "Model Accuracy", accuracy_display, to_hex(PRIMARY_COLOR)
    )
    machines = create_kpi_card(
        "Machines Analysed", str(total_machines), to_hex(PRIMARY_COLOR)
    )

    # Dynamic color for the Critical Machines card: green when nothing is
    # critical, orange once critical machines exist but stay under 10% of
    # the fleet, red once they hit/exceed that threshold. Computed from
    # results_df-derived counts rather than a fixed color, so the card's
    # color always matches how bad the fleet's situation actually is.
    if critical_count == 0:
        critical_card_color = COLOR_HEALTHY_GREEN
    elif critical_count < total_machines * 0.10:
        critical_card_color = COLOR_WARNING_ORANGE
    else:
        critical_card_color = COLOR_CRITICAL_RED

    critical_card = create_kpi_card(
        "Critical Machines", str(critical_count), to_hex(critical_card_color)
    )

    # Average Confidence replaces the old Immediate Shutdown card — that
    # figure is already covered by the Maintenance Summary/Recommendations
    # sections, so this card surfaces a metric not shown anywhere else.
    confidence_card = create_kpi_card(
        "Average Confidence",
        f"{avg_confidence:.1f}%",
        to_hex(PRIMARY_COLOR),
    )

    # TASK 19 — Overall Fleet Risk card, colored using the same
    # standardized palette as the other dynamic KPI cards above.
    fleet_risk_card = create_kpi_card(
        "Overall Fleet Risk", fleet_risk, to_hex(risk_color)
    )

    kpi_layout = Table([
        [accuracy, machines],
        [critical_card, confidence_card],
        [fleet_risk_card, ""],
    ], colWidths=[3.2 * inch, 3.2 * inch], rowHeights=[1.35 * inch, 1.35 * inch, 1.35 * inch])

    kpi_layout.setStyle(TableStyle([
        ("SPAN", (0, 2), (1, 2)),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    # KeepTogether so this grid moves to the next page as a whole, rather
    # than splitting a row of KPI cards across a page break, now that it
    # no longer sits behind a forced PageBreak().
    elements.append(KeepTogether(kpi_layout))
    elements.append(Spacer(1, SPACE_AFTER_SECTION))

    # ==========================
    # Health Distribution (Task 14.4/14.5 layout)
    # ==========================

    elements.append(Paragraph("Health Distribution", styles["SectionHeading"]))
    elements.append(Spacer(1, SPACE_AFTER_HEADING))
    elements.extend(make_chart_section(
        chart_paths["health_distribution"],
        "Figure 1. Health Distribution of Predicted Machine Conditions.",
        styles,
    ))

    # Model Information previously lived here (right after the Health
    # Distribution chart). It's been moved up onto the Executive Summary
    # page — see above — since that spot on its own reliably left a
    # near-empty page behind it. Prediction Summary now follows the
    # Health Distribution chart directly, on whatever page ReportLab's
    # natural flow puts it, rather than behind a forced PageBreak.
    # ==========================

    # ==========================
    # Prediction Summary
    # ==========================

    elements.append(Paragraph("Prediction Summary", styles["SectionHeading"]))
    elements.append(Spacer(1, SPACE_AFTER_HEADING))

    prediction_table_data = [["Health Stage", "Machine Count"]]
    for _, row in prediction_summary.iterrows():
        prediction_table_data.append([row["Health Stage"], str(row["Count"])])

    elements.append(make_standard_table(prediction_table_data))
    elements.append(Spacer(1, SPACE_AFTER_SECTION))

    # ==========================
    # Maintenance Summary
    # ==========================

    elements.append(Paragraph("Maintenance Summary", styles["SectionHeading"]))
    elements.append(Spacer(1, SPACE_AFTER_HEADING))

    maintenance_table_data = [["Maintenance Action", "Machine Count"]]
    for _, row in maintenance_summary.iterrows():
        maintenance_table_data.append([row["Maintenance"], str(row["Count"])])

    elements.append(make_standard_table(maintenance_table_data))
    elements.append(Spacer(1, SPACE_AFTER_SECTION))

    # The Maintenance Distribution chart was already being generated on
    # every build (see generate_maintenance_distribution_chart above) but
    # was never placed into the document body — it existed only as a PNG
    # on disk. It's added here, directly under its matching summary table,
    # using the same make_chart_section layout as every other chart.
    elements.append(Paragraph("Maintenance Distribution", styles["SectionHeading"]))
    elements.append(Spacer(1, SPACE_AFTER_HEADING))
    elements.extend(make_chart_section(
        chart_paths["maintenance_distribution"],
        "Figure 2. Maintenance Action Distribution Across the Fleet.",
        styles,
    ))

    # The PageBreak() previously here forced Confidence Distribution onto
    # a fresh page even when the Maintenance Distribution chart above it
    # already left little content behind, producing a near-empty page in
    # between. Removed so Confidence Distribution flows naturally onto
    # whatever page has room, instead of a forced blank one.


    # ==========================
    # Confidence Distribution
    # ==========================

    elements.append(Paragraph("Confidence Distribution", styles["SectionHeading"]))
    elements.append(Spacer(1, SPACE_AFTER_HEADING))
    elements.extend(make_chart_section(
        chart_paths["confidence_distribution"],
        "Figure 3. Prediction Confidence Distribution Across Analysed Machines.",
        styles,
    ))

    # ==========================
    # TASK 21 — CONFIDENCE STATISTICS
    # All four figures (plus the Step 7 quality row) come from the same
    # `confidence` Series computed above, so this table can never drift
    # from the chart directly above it. confidence_level is reused as-is
    # from the KPI section rather than recomputed — it already applies
    # the same Excellent/High/Moderate/Low thresholds this step needs.
    # ==========================

    confidence_stats = [
        ["Statistic", "Value"],
        ["Average", f"{avg_confidence:.2f}%"],
        ["Minimum", f"{min_confidence:.2f}%"],
        ["Maximum", f"{max_confidence:.2f}%"],
        ["Standard Deviation", f"{std_confidence:.2f}%"],
        ["Confidence Quality", confidence_level.upper()],
    ]

    if confidence_level == "Excellent":
        confidence_message = "The model demonstrates excellent prediction confidence."
    elif confidence_level == "High":
        confidence_message = "The model demonstrates high prediction confidence."
    elif confidence_level == "Moderate":
        confidence_message = "The model demonstrates acceptable prediction confidence."
    else:
        confidence_message = "Prediction confidence is relatively low."

    # KeepTogether so this table can't split across a page boundary with
    # its header row left behind on the prior page (Tables split by row
    # by default) — it now moves to the next page as a whole if it
    # doesn't fit, rather than splitting awkwardly.
    elements.append(
        KeepTogether([
            make_standard_table(confidence_stats, col_widths=[2.2 * inch, 1.8 * inch]),
            Spacer(1, SPACE_AFTER_CONTENT),
            Paragraph(confidence_message, styles["Body"]),
        ])
    )
    elements.append(Spacer(1, SPACE_AFTER_SECTION))

    # ==========================
    # Feature Importance
    # ==========================

    # PageBreak() removed here — it was forcing Feature Importance onto a
    # fresh page even when the Confidence Statistics table above left
    # most of the current page unused, producing a near-empty page in
    # between (the same pattern as the Maintenance/Confidence Distribution
    # fix above). Feature Importance now flows onto whichever page has
    # room.

    elements.append(Paragraph("Feature Importance", styles["SectionHeading"]))
    elements.append(Spacer(1, SPACE_AFTER_HEADING))
    elements.extend(make_chart_section(
        chart_paths["feature_importance"],
        "Figure 4. Feature Importance Analysis for the XGBoost Model.",
        styles,
    ))

    # ==========================
    # TASK 22 — TOP FEATURE SUMMARY
    # Reads the same CSV/columns as generate_feature_importance_chart
    # above (via load_feature_importance), so the "top feature" named
    # here always matches the tallest/highlighted bar in the chart.
    # top_importance_pct is the top feature's share of the sum of all
    # importances in the file, rather than assuming the raw values are
    # already 0-1 fractions.
    # ==========================

    feature_importance_df = load_feature_importance(chart_paths["feature_importance_csv"])
    top_feature = str(feature_importance_df.iloc[0]["feature"])
    total_importance = feature_importance_df["importance"].sum()
    top_importance_pct = (
        (feature_importance_df.iloc[0]["importance"] / total_importance * 100)
        if total_importance else 0
    )

    interpretation = FEATURE_EXPLANATIONS.get(
        top_feature.lower(),
        "Feature contributes significantly to model prediction.",
    )

    # Task 28 — the Interpretation sentence was previously a table row,
    # but interpretation text is long-form prose and doesn't fit the
    # fixed-width "Metric | Value" table format cleanly (it either
    # overflowed the cell or forced awkward wrapping). The table now
    # holds only the two short, tabular metrics; the interpretation is
    # rendered as its own paragraph directly below, alongside
    # feature_message.
    feature_summary = [
        ["Metric", "Value"],
        ["Top Feature", top_feature.upper()],
        ["Importance", f"{top_importance_pct:.1f}%"],
    ]

    elements.append(
        make_standard_table(feature_summary, col_widths=[1.6 * inch, 4.9 * inch])
    )
    elements.append(Spacer(1, SPACE_AFTER_CONTENT))

    elements.append(Paragraph(interpretation, styles["Body"]))
    elements.append(Spacer(1, SPACE_AFTER_CONTENT))

    feature_message = (
        f"<b>{top_feature.upper()}</b> is the strongest predictor in the XGBoost "
        f"model, contributing <b>{top_importance_pct:.1f}%</b> of the total feature "
        f"importance."
    )
    elements.append(Paragraph(feature_message, styles["Body"]))
    elements.append(Spacer(1, SPACE_AFTER_SECTION))

    # ==========================
    # Operational Insights
    # ==========================

    elements.append(Paragraph("Operational Insights", styles["SectionHeading"]))
    elements.append(Spacer(1, SPACE_AFTER_HEADING))

    # Every bullet below is built from the KPI variables computed once near
    # the top of the function, so if results_df changes, this list updates
    # automatically — nothing here is a hardcoded figure. Numeric values
    # are wrapped in <b> so key figures stand out while the surrounding
    # sentence stays regular weight.
    operational_insights = [
        f"Fleet Health: <b>{healthy_pct:.1f}%</b> of machines are operating in a healthy state.",
        f"Critical Assets: <b>{critical_count}</b> machines (<b>{critical_pct:.1f}%</b>) require urgent maintenance.",
        f"Immediate Shutdown Required: <b>{failure_count}</b> machines (<b>{failure_pct:.1f}%</b>) are at imminent risk.",
        f"Scheduled Inspection: <b>{inspection_count}</b> machines are recommended for preventive inspection.",
    ]

    # Step 5 — maintenance workload (Critical + Imminent Failure combined).
    operational_insights.append(
        f"<b>{maintenance_required}</b> machines (<b>{maintenance_pct:.1f}%</b>) require maintenance within the current planning cycle."
    )

    # Step 6 — qualitative confidence assessment, not just a bare number.
    operational_insights.append(
        f"Model confidence is {confidence_level} (<b>{avg_confidence:.1f}%</b>)."
    )

    # TASK 19 — Overall Fleet Risk Level bullet.
    operational_insights.append(
        f"Overall Fleet Risk Level: <b>{fleet_risk}</b>"
    )

    for insight in operational_insights:
        elements.append(
            Paragraph(f"&bull; {insight}", styles["InsightsBody"])
        )
        elements.append(Spacer(1, 0.08 * inch))

    elements.append(Spacer(1, SPACE_AFTER_HEADING))

    # Step 7 — short, action-oriented takeaway derived from the same counts.
    elements.append(Paragraph(priority, styles["InsightsBody"]))
    elements.append(Spacer(1, SPACE_AFTER_SECTION))

    # ==========================
    # Maintenance Recommendations
    # ==========================

    recommendation_heading = Paragraph("Maintenance Recommendations", styles["SectionHeading"])

    # Table is generated directly from RECOMMENDATION_MAPPING and
    # PRIORITY_MAPPING (in HEALTH_STAGE_ORDER) rather than a hand-typed
    # table, so a row exists for every defined prediction class and
    # editing either mapping is the only thing ever needed to change what
    # the table shows. The Step-4 validation earlier in this function
    # already guarantees every class in results_df has an entry here, so
    # this loop can't silently skip a class that's actually present in
    # the data.
    recommendation_data = [["Prediction", "Recommended Action", "Priority"]]

    for prediction in HEALTH_STAGE_ORDER:
        action = RECOMMENDATION_MAPPING[prediction]
        recommendation_data.append([
            prediction,
            action,
            PRIORITY_MAPPING[prediction],
        ])

    recommendation_table = make_standard_table(
        recommendation_data, col_widths=[2.0 * inch, 2.7 * inch, 1.8 * inch]
    )

    recommendation_note = Paragraph(
        "Maintenance recommendations are generated automatically from the "
        "prediction class mapping, ensuring consistency between model "
        "outputs and operational actions.",
        styles["Body"],
    )

    elements.append(
        KeepTogether([
            recommendation_heading,
            Spacer(1, SPACE_AFTER_HEADING),
            recommendation_table,
            Spacer(1, SPACE_AFTER_CONTENT),
            recommendation_note,
        ])
    )

    elements.append(Spacer(1, SPACE_AFTER_SECTION))

    # ==========================
    # Conclusion
    # ==========================

    elements.append(PageBreak())

    conclusion_heading = Paragraph("Conclusion", styles["SectionHeading"])

    # TASK 23 — Dynamic conclusion, built entirely from the KPI variables
    # computed once near the top of the function. Uses fleet_risk (Task 19)
    # as the single risk classification shown here, rather than a second
    # "overall_status" label computed on different thresholds.
    conclusion_text = f"""
    The EdgePulse predictive maintenance system analysed <b>{total_machines}</b>
    rotating machinery records using an XGBoost-based machine learning
    model.<br/><br/>

    The analysis identified <b>{healthy_count}</b> healthy machines
    ({healthy_pct:.1f}%), <b>{critical_count}</b> critical machines
    ({critical_pct:.1f}%), and <b>{failure_count}</b> machines
    ({failure_pct:.1f}%) requiring immediate shutdown.<br/><br/>

    The model achieved an average prediction confidence of
    <b>{avg_confidence:.1f}%</b> and classified the overall fleet risk as
    <b>{fleet_risk}</b>.<br/><br/>

    Based on these findings, maintenance efforts should prioritise
    <b>{maintenance_required}</b> high-risk machines to minimise unexpected
    equipment failures and reduce operational downtime.
    """

    conclusion_body = Paragraph(conclusion_text, styles["InsightsBody"])

    elements.append(
        KeepTogether([
            conclusion_heading,
            Spacer(1, SPACE_AFTER_HEADING),
            conclusion_body,
        ])
    )

    elements.append(Spacer(1, SPACE_AFTER_SECTION))

    # ==========================
    # Business Impact
    # ==========================

    business_impact = [
        "Reduced unplanned equipment downtime.",
        "Improved maintenance scheduling.",
        "Lower maintenance costs through predictive intervention.",
        "Enhanced operational reliability and asset utilisation.",
    ]

    business_impact_block = [
        Paragraph("Business Impact", styles["SubHeading"]),
        Spacer(1, SPACE_AFTER_HEADING),
    ]
    for item in business_impact:
        business_impact_block.append(Paragraph(f"&bull; {item}", styles["InsightsBody"]))
        business_impact_block.append(Spacer(1, 0.08 * inch))

    elements.append(KeepTogether(business_impact_block))
    elements.append(Spacer(1, SPACE_AFTER_SECTION))

    # ==========================
    # Future Scope
    # ==========================

    future_scope = [
        "Real-time IoT sensor integration.",
        "Edge deployment on industrial devices.",
        "Automated maintenance scheduling.",
        "Cloud-based fleet monitoring dashboard.",
    ]

    future_scope_block = [
        Paragraph("Future Scope", styles["SubHeading"]),
        Spacer(1, SPACE_AFTER_HEADING),
    ]
    for item in future_scope:
        future_scope_block.append(Paragraph(f"&bull; {item}", styles["InsightsBody"]))
        future_scope_block.append(Spacer(1, 0.08 * inch))

    elements.append(KeepTogether(future_scope_block))
    elements.append(Spacer(1, SPACE_AFTER_SECTION))

    # ==========================
    # Closing Statement
    # ==========================

    closing = (
        "EdgePulse demonstrates how explainable AI and predictive analytics "
        "can transform industrial maintenance by enabling proactive "
        "decision-making, improving asset reliability, and reducing "
        "operational costs."
    )

    elements.append(Paragraph(closing, styles["Body"]))
    elements.append(Spacer(1, SPACE_AFTER_SECTION))

    doc.build(
        elements,
        onFirstPage=add_footer,
        onLaterPages=add_footer,
    )

    return output_path


def add_footer(canvas, doc):
    """Consistent footer on every page: same font, same accent line color,
    same placement, aligned to the document's actual left/right margins
    (Task 14 Steps 1 & 6)."""
    canvas.saveState()

    page_width, _ = doc.pagesize
    left_edge = PAGE_LEFT_MARGIN
    right_edge = page_width - PAGE_RIGHT_MARGIN

    # thin accent rule above the footer text, using the single theme color
    canvas.setStrokeColor(PRIMARY_COLOR)
    canvas.setLineWidth(0.75)
    canvas.line(left_edge, 0.62 * inch, right_edge, 0.62 * inch)

    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(COLOR_GREY)

    canvas.drawString(
        left_edge,
        0.5 * inch,
        "EdgePulse Predictive Maintenance System | Confidential",
    )

    canvas.drawRightString(
        right_edge,
        0.5 * inch,
        f"Page {doc.page}",
    )

    canvas.restoreState()