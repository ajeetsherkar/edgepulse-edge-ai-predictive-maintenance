"""
EdgePulse Chart Utilities

Reusable Plotly chart functions for:

- Dashboard
- Executive PDF Report
- Future APIs
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from utils.constants import *


def create_health_chart(health_counts, color_map=None):
    """
    Bar chart showing machine counts per health stage.

    health_counts: DataFrame with columns ["Health Stage", "Count"]
    color_map: optional dict mapping health stage -> hex color
    """
    fig = px.bar(
        health_counts,
        x="Health Stage",
        y="Count",
        color="Health Stage",
        color_discrete_map=color_map,
        text="Count",
    )

    fig.update_traces(textposition="outside")

    fig.update_layout(
        height=450,
        showlegend=False,
        xaxis_title="Health Stage",
        yaxis_title="Machine Count",
    )

    return fig


def create_feature_importance_chart(feature_df):
    """
    Horizontal bar chart showing model feature importance.
    """
    feature_df = feature_df.copy()
    # Standardize column names
    feature_df.columns = feature_df.columns.str.strip().str.lower()
    sorted_df = feature_df.sort_values(
        "importance",
        ascending=True
    )
    fig = px.bar(
        sorted_df,
        x="importance",
        y="feature",
        orientation="h",
        text="importance",
    )
    fig.update_traces(
        texttemplate="%{text:.3f}",
        textposition="outside"
    )
    fig.update_layout(
        height=450,
        xaxis_title="Importance",
        yaxis_title="Feature",
    )
    return fig


def create_confidence_chart(results_df):
    """
    Histogram showing the distribution of prediction confidence scores.

    results_df: DataFrame with a "Confidence (%)" column
    """
    fig = px.histogram(
        results_df,
        x="Confidence (%)",
        nbins=20,
    )

    fig.update_layout(
        height=450,
        xaxis_title="Confidence (%)",
        yaxis_title="Number of Machines",
        bargap=0.1,
    )

    return fig


def create_maintenance_chart(results_df):
    """
    Maintenance Action Distribution
    """

    fig = px.bar(
        x=results_df["Maintenance"],
        y=results_df["Count"],
        text=results_df["Count"],
    )

    fig.update_traces(textposition="outside")

    fig.update_layout(
        height=450,
        showlegend=False,
        xaxis_title="Maintenance Action",
        yaxis_title="Machine Count",
    )

    return fig


# ======================================
# Future Charts
# ======================================

# create_edge_architecture()

# create_model_comparison()

# create_sensor_timeline()

# create_rul_chart()