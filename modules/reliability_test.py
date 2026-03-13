"""
reliability_test.py - Cronbach's Alpha and Alpha-if-Item-Deleted
"""
import pandas as pd
import numpy as np


def cronbach_alpha(df, columns):
    """
    Calculate Cronbach's Alpha for a set of items.
    Returns the alpha coefficient.
    """
    data = df[columns].dropna()
    n_items = len(columns)
    if n_items < 2:
        return None
    item_variances = data.var(axis=0, ddof=1)
    total_variance = data.sum(axis=1).var(ddof=1)
    alpha = (n_items / (n_items - 1)) * (1 - item_variances.sum() / total_variance)
    return round(float(alpha), 4)


def alpha_if_item_deleted(df, columns):
    """
    Calculate Cronbach's Alpha if each item is deleted.
    Returns DataFrame with columns: Item, Alpha_jika_Dihapus
    """
    results = []
    for col in columns:
        remaining = [c for c in columns if c != col]
        if len(remaining) < 2:
            alpha = None
        else:
            alpha = cronbach_alpha(df, remaining)
        results.append({
            "Item": col,
            "Alpha Jika Dihapus": alpha
        })
    return pd.DataFrame(results)


def interpret_alpha(alpha):
    """Return Indonesian interpretation of Cronbach's Alpha."""
    if alpha is None:
        return "Tidak dapat dihitung"
    if alpha >= 0.90:
        return "Sangat Baik (≥ 0.90)"
    elif alpha >= 0.80:
        return "Baik (0.80–0.89)"
    elif alpha >= 0.70:
        return "Cukup (0.70–0.79)"
    elif alpha >= 0.60:
        return "Kurang (0.60–0.69)"
    else:
        return "Tidak Reliabel (< 0.60)"


def interpret_alpha_color(alpha):
    """Return color based on alpha value."""
    if alpha is None:
        return "gray"
    if alpha >= 0.80:
        return "green"
    elif alpha >= 0.70:
        return "orange"
    elif alpha >= 0.60:
        return "orangered"
    else:
        return "red"
