"""
2_Pemeriksaan_Data.py - Pemeriksaan kualitas data dan distribusi jawaban
"""
import streamlit as st
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules.visualizations import (
    plot_missing_heatmap, plot_response_distribution,
    plot_boxplot, plot_likert_stacked
)

st.set_page_config(page_title="Pemeriksaan Data", page_icon="🔍", layout="wide")

st.title("🔍 Pemeriksaan Kualitas Data")
st.markdown("Analisis kualitas data survei Anda sebelum menjalankan uji statistik.")

if "df" not in st.session_state or st.session_state["df"] is None:
    st.warning("⚠️ Belum ada data. Silakan pergi ke halaman **Upload Data** terlebih dahulu.")
    st.stop()

df           = st.session_state["df"]
likert_cols  = st.session_state.get("likert_cols", [])
scale_min    = st.session_state.get("scale_min", 1)
scale_max    = st.session_state.get("scale_max", 4)

if not likert_cols:
    st.warning("⚠️ Tidak ada item Likert yang dipilih. Konfirmasi item di halaman Upload Data.")
    st.stop()

# ── 1. Missing Value ───────────────────────────────────────────────────────────
st.markdown("### 🟥 Peta Nilai Kosong (Missing Value)")
st.caption("Warna merah = nilai kosong. Idealnya tidak ada warna merah sama sekali.")

missing_count = df[likert_cols].isnull().sum().sum()
if missing_count == 0:
    st.success("✅ Tidak ditemukan nilai kosong pada item Likert. Data lengkap!")
else:
    st.warning(f"⚠️ Ditemukan **{missing_count}** nilai kosong pada item Likert.")
    st.plotly_chart(plot_missing_heatmap(df, likert_cols), use_container_width=True)

# ── 2. Distribusi Jawaban ──────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📊 Distribusi Jawaban Responden")
st.caption("Pola yang baik biasanya berbentuk lonceng (normal) atau simetris.")

tab1, tab2 = st.tabs(["📊 Histogram", "📊 Stacked Bar (%)"])

with tab1:
    selected = st.multiselect(
        "Pilih item untuk ditampilkan:",
        options=likert_cols,
        default=likert_cols[:min(5, len(likert_cols))],
    )
    if selected:
        st.plotly_chart(plot_response_distribution(df, selected), use_container_width=True)

with tab2:
    st.plotly_chart(plot_likert_stacked(df, likert_cols, scale_min, scale_max), use_container_width=True)

# ── 3. Boxplot ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📦 Boxplot Skor Pertanyaan")
st.caption("Kotak = 50% data tengah. Garis tengah = median. Titik di luar = outlier.")
st.plotly_chart(plot_boxplot(df, likert_cols), use_container_width=True)

# ── 4. Statistik Deskriptif ────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📋 Statistik Deskriptif")

import pandas as pd
desc = df[likert_cols].describe().T.round(3)
desc.index.name = "Item"
desc.columns    = ["N Valid", "Rata-rata", "Std. Dev", "Min", "Q1", "Median", "Q3", "Max"]
st.dataframe(desc, use_container_width=True,
        hide_index=True,
    )

# ── 5. Pertanyaan Negatif ──────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🔄 Pengaturan Pertanyaan Negatif (Reverse Item)")

with st.container(border=True):
    st.markdown(
        "**Apa itu pertanyaan negatif?** Pertanyaan yang penilaiannya berlawanan arah. "
        f"Contoh: *'Saya tidak puas dengan layanan.'* "
        f"Skor akan dibalik: **skor_baru = ({scale_max} + {scale_min}) – skor_asli**"
    )

reverse_cols = st.multiselect(
    "Pilih pertanyaan yang bersifat NEGATIF:",
    options=likert_cols,
    default=st.session_state.get("reverse_cols", []),
)

if reverse_cols:
    st.info(
        f"🔁 **{len(reverse_cols)} pertanyaan** akan dibalik. "
        f"Contoh skala {scale_min}–{scale_max}: "
        f"skor 1 → {scale_max + scale_min - 1}, skor {scale_max} → 1"
    )

if st.button("💾 Simpan Pengaturan"):
    st.session_state["reverse_cols"] = reverse_cols
    st.success(f"✅ Tersimpan. {len(reverse_cols)} pertanyaan ditandai negatif.")
