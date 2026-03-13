"""
6_Insight_Survei.py - Dashboard visual insight data survei
"""
import streamlit as st
import pandas as pd
import numpy as np
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from modules.reverse_items import apply_reverse_items
from modules.likert_detection import interpret_score, get_likert_interpretation
from modules.visualizations import (
    make_short_labels,
    plot_mean_scores,
    plot_correlation_heatmap,
    plot_likert_stacked,
    plot_radar_chart,
)

st.set_page_config(page_title="Insight Survei", page_icon="📈", layout="wide")


def show_legend(cols):
    """Tampilkan tabel kode → pertanyaan lengkap jika label disingkat."""
    short_map, legend_df = make_short_labels(cols)
    if any(short_map[c] != c for c in cols):
        with st.expander("📖 Keterangan kode pertanyaan di grafik"):
            st.dataframe(legend_df, use_container_width=True, hide_index=True)


# ── Check session ──────────────────────────────────────────────────────────────
st.title("📈 Dashboard Insight Survei")
st.markdown("Eksplorasi visual lengkap hasil survei Anda dalam satu dashboard terpadu.")

if "df" not in st.session_state or st.session_state["df"] is None:
    st.warning("⚠️ Belum ada data. Silakan upload di halaman **Upload Data**.")
    st.stop()

df           = st.session_state["df"]
likert_cols  = st.session_state.get("likert_cols", [])
scale_min    = st.session_state.get("scale_min", 1)
scale_max    = st.session_state.get("scale_max", 4)
reverse_cols = st.session_state.get("reverse_cols", [])

if not likert_cols:
    st.warning("⚠️ Tidak ada item Likert yang dipilih.")
    st.stop()

df_analysis = apply_reverse_items(df, likert_cols, reverse_cols, scale_min, scale_max)

# ── Summary Metrics ────────────────────────────────────────────────────────────
st.markdown("### 📊 Ringkasan Keseluruhan")
overall_mean   = df_analysis[likert_cols].mean().mean()
overall_interp = interpret_score(overall_mean, scale_min, scale_max)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Jumlah Responden",       len(df))
c2.metric("Jumlah Item Dianalisis", len(likert_cols))
c3.metric("Rata-rata Keseluruhan",  f"{overall_mean:.2f}")
c4.metric("Interpretasi",           overall_interp)

# ── 1. Rata-rata Skor Per Item ─────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🎯 Rata-rata Skor Per Pertanyaan")
st.caption(
    "Hijau = skor di atas tengah skala (positif). "
    "Merah = skor di bawah tengah skala (perlu perhatian). "
    "Arahkan kursor ke batang untuk melihat pertanyaan lengkap."
)
st.plotly_chart(
    plot_mean_scores(df_analysis, likert_cols, scale_min, scale_max),
    use_container_width=True,
)
show_legend(likert_cols)

# ── 2. Interpretasi Per Item ───────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📋 Interpretasi Skor Per Item")

thresholds = get_likert_interpretation(scale_min, scale_max)
parts = []
prev  = scale_min
for upper, label in thresholds:
    parts.append(f"{round(prev, 2)}–{round(upper, 2)} = {label}")
    prev = upper + 0.01
st.caption(f"Skala {scale_min}–{scale_max}: " + " | ".join(parts))

short_map, legend_df = make_short_labels(likert_cols)
item_means  = df_analysis[likert_cols].mean()
interp_rows = []
for col in likert_cols:
    mean_val = round(float(item_means[col]), 3)
    interp   = interpret_score(mean_val, scale_min, scale_max)
    interp_rows.append({
        "Kode":         short_map.get(col, col),
        "Pertanyaan":   col if short_map.get(col, col) == col else col[:60] + ("…" if len(col) > 60 else ""),
        "Rata-rata":    mean_val,
        "Interpretasi": interp,
    })

interp_df = pd.DataFrame(interp_rows)

def color_interp(val):
    if "Baik" in str(val):
        return "background-color:#d4edda;color:#155724;"
    return "background-color:#f8d7da;color:#721c24;"

st.dataframe(
    interp_df.style.applymap(color_interp, subset=["Interpretasi"]),
    use_container_width=True,
    hide_index=True,
)

# ── 3. Distribusi Jawaban ──────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📊 Distribusi Persentase Jawaban")
st.caption(
    "Grafik ini menunjukkan persentase setiap pilihan jawaban per pertanyaan. "
    "Arahkan kursor ke batang untuk melihat pertanyaan lengkap."
)
st.plotly_chart(
    plot_likert_stacked(df_analysis, likert_cols, scale_min, scale_max),
    use_container_width=True,
)
show_legend(likert_cols)

# ── 4. Radar Chart (hanya jika EFA sudah dijalankan) ──────────────────────────
if "efa_loadings" in st.session_state:
    st.markdown("---")
    st.markdown("### 🕸️ Radar Chart: Rata-rata per Faktor")
    st.caption("Membandingkan rata-rata skor antar konstruk/faktor dari Analisis Faktor.")

    from modules.efa_analysis import get_factor_assignments
    factor_names = st.session_state.get("factor_names", {})
    assignments  = get_factor_assignments(st.session_state["efa_loadings"], threshold=0.40)
    factor_items = {}
    for item, (factor, _) in assignments.items():
        if factor != "Tidak ada":
            label = factor_names.get(factor, factor)
            factor_items.setdefault(label, []).append(item)

    if len(factor_items) >= 3:
        radar_data = {
            fname: df_analysis[items].mean().mean()
            for fname, items in factor_items.items()
        }
        st.plotly_chart(plot_radar_chart(radar_data), use_container_width=True)
    else:
        st.info("ℹ️ Radar chart membutuhkan minimal 3 faktor.")

# ── 5. Heatmap Korelasi ────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🌡️ Heatmap Korelasi Antar Item")
st.caption(
    "Biru = korelasi positif (item cenderung naik bersamaan). "
    "Merah = korelasi negatif. "
    "Item berkorelasi tinggi kemungkinan mengukur hal yang sama."
)
st.plotly_chart(
    plot_correlation_heatmap(df_analysis, likert_cols),
    use_container_width=True,
)
show_legend(likert_cols)

# ── 6. Top & Bottom Items ──────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🏆 Item Skor Tertinggi & Terendah")

sorted_means = item_means.sort_values(ascending=False)
c1, c2       = st.columns(2)

with c1:
    st.markdown("**🔝 5 Item Skor Tertinggi:**")
    top5 = sorted_means.head(5).reset_index()
    top5.columns = ["Pertanyaan", "Rata-rata"]
    top5.insert(0, "Kode", [short_map.get(q, q) for q in top5["Pertanyaan"]])
    top5["Rata-rata"] = top5["Rata-rata"].round(3)
    st.dataframe(top5, use_container_width=True, hide_index=True)

with c2:
    st.markdown("**🔻 5 Item Skor Terendah:**")
    bot5 = sorted_means.tail(5).reset_index()
    bot5.columns = ["Pertanyaan", "Rata-rata"]
    bot5.insert(0, "Kode", [short_map.get(q, q) for q in bot5["Pertanyaan"]])
    bot5["Rata-rata"] = bot5["Rata-rata"].round(3)
    st.dataframe(bot5, use_container_width=True, hide_index=True)
