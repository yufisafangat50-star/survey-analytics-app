"""
reverse_items.py - Handles reverse-scored (negative) Likert items
"""
import pandas as pd
import numpy as np


def reverse_score(series, scale_min, scale_max):
    """
    Reverse score a Likert item.
    Formula: new_score = (max + min) - original_score
    """
    return (scale_max + scale_min) - series


def apply_reverse_items(df, columns, reverse_cols, scale_min, scale_max):
    """
    Apply reverse scoring to selected columns.
    Returns a new DataFrame with reversed items.
    """
    df_reversed = df[columns].copy()
    for col in reverse_cols:
        if col in df_reversed.columns:
            df_reversed[col] = reverse_score(df_reversed[col], scale_min, scale_max)
    return df_reversed
