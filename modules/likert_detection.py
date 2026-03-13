"""
likert_detection.py - Automatically detects Likert scale items from a DataFrame
"""
import pandas as pd
import numpy as np


def detect_likert_items(df, max_unique=7, min_val=1, max_val=7):
    """
    Detect columns that are likely Likert scale items.
    Rules:
    - Must be numeric
    - Unique values <= max_unique
    - All values within [min_val, max_val]
    Returns list of column names.
    """
    likert_cols = []
    for col in df.select_dtypes(include=[np.number]).columns:
        series = df[col].dropna()
        if len(series) == 0:
            continue
        unique_vals = series.nunique()
        col_min = series.min()
        col_max = series.max()
        if unique_vals <= max_unique and col_min >= min_val and col_max <= max_val:
            likert_cols.append(col)
    return likert_cols


def get_likert_scale_range(df, columns):
    """Detect the Likert scale range (e.g., 1-4, 1-5, 1-7) from the data."""
    if not columns:
        return 1, 4
    all_vals = df[columns].values.flatten()
    all_vals = all_vals[~np.isnan(all_vals)]
    return int(np.nanmin(all_vals)), int(np.nanmax(all_vals))


def get_likert_interpretation(scale_min, scale_max):
    """
    Returns interpretation thresholds based on scale range.
    Returns list of (upper_bound, label) tuples.
    """
    scale_range = scale_max - scale_min + 1
    step = (scale_max - scale_min) / 4
    thresholds = [
        (scale_min + step * 1, "Sangat Buruk"),
        (scale_min + step * 2, "Buruk"),
        (scale_min + step * 3, "Baik"),
        (scale_max, "Sangat Baik"),
    ]
    return thresholds


def interpret_score(score, scale_min, scale_max):
    """Return text interpretation for a mean score."""
    thresholds = get_likert_interpretation(scale_min, scale_max)
    for upper, label in thresholds:
        if score <= upper:
            return label
    return "Sangat Baik"
