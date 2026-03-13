"""
validity_test.py - Corrected Item-Total Correlation for questionnaire validity
"""
import pandas as pd
import numpy as np
from scipy import stats


def corrected_item_total_correlation(df, columns):
    """
    Calculate corrected item-total correlation (CITC) for each item.
    CITC = correlation of item with sum of all OTHER items.
    Returns DataFrame with columns: Item, CITC, Valid
    """
    results = []
    data = df[columns].dropna()
    for col in columns:
        other_cols = [c for c in columns if c != col]
        item_scores = data[col]
        total_scores = data[other_cols].sum(axis=1)
        r, p_value = stats.pearsonr(item_scores, total_scores)
        results.append({
            "Item": col,
            "Korelasi Item-Total": round(r, 4),
            "p-value": round(p_value, 4),
            "Status": "Valid ✅" if r > 0.30 else "Tidak Valid ❌"
        })
    return pd.DataFrame(results)


def get_validity_summary(validity_df):
    """Return counts of valid and invalid items."""
    valid = (validity_df["Status"] == "Valid ✅").sum()
    invalid = (validity_df["Status"] == "Tidak Valid ❌").sum()
    return valid, invalid
