"""
validity_test.py - Corrected Item-Total Correlation for questionnaire validity
"""
import pandas as pd
import numpy as np
from scipy import stats


def get_combined_interpretation(r, p_value, threshold=0.30, alpha=0.05):
    """
    Interpretasi gabungan berdasarkan nilai r dan p-value.
    Menghasilkan label ringkas + penjelasan ramah untuk semua pengguna.
    """
    valid  = r > threshold
    sig    = p_value < alpha

    if valid and sig:
        return (
            "✅ Valid & Signifikan",
            "Pertanyaan ini mengukur hal yang sama dengan kuesioner secara "
            "keseluruhan, dan hasilnya dapat dipercaya."
        )
    elif valid and not sig:
        return (
            "⚠️ Valid tapi Belum Meyakinkan",
            "Pertanyaan cukup relevan, namun butuh lebih banyak responden "
            "untuk memastikan hasilnya."
        )
    elif not valid and sig:
        return (
            "ℹ️ Kurang Relevan",
            "Pertanyaan kurang mencerminkan topik kuesioner, meskipun "
            "polanya konsisten di semua responden."
        )
    else:
        return (
            "❌ Tidak Valid",
            "Pertanyaan tidak mencerminkan topik kuesioner dan hasilnya "
            "tidak dapat diandalkan."
        )


def corrected_item_total_correlation(df, columns, threshold=0.30):
    """
    Hitung Corrected Item-Total Correlation (CITC) untuk setiap item.
    CITC = korelasi item dengan jumlah skor semua item LAINNYA.
    """
    results = []
    data    = df[columns].dropna()

    for col in columns:
        other_cols   = [c for c in columns if c != col]
        item_scores  = data[col]
        total_scores = data[other_cols].sum(axis=1)
        r, p_value   = stats.pearsonr(item_scores, total_scores)

        label, penjelasan = get_combined_interpretation(r, p_value, threshold)

        results.append({
            "Item":                col,
            "Korelasi Item-Total": round(r, 4),
            "p-value":             round(p_value, 4),
            "Interpretasi":        label,
            "Penjelasan":          penjelasan,
            # kolom lama dipertahankan agar tidak merusak kode lain
            "Status":              "Valid ✅" if r > threshold else "Tidak Valid ❌",
        })

    return pd.DataFrame(results)


def get_validity_summary(validity_df):
    """Kembalikan jumlah item valid dan tidak valid."""
    valid   = (validity_df["Status"] == "Valid ✅").sum()
    invalid = (validity_df["Status"] == "Tidak Valid ❌").sum()
    return valid, invalid
