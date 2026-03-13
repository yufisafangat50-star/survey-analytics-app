"""
1_Upload_Data.py - Halaman upload dan preview data survei
"""
import streamlit as st
import pandas as pd
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules.data_loader import load_data, get_data_summary, get_numeric_columns
from modules.likert_detection import detect_likert_items, get_likert_scale_range

st.set_page_config(page_title="Upload Data", page_icon="📂", layout="wide")

st.title("📂 Upload Data Survei")
st.markdown("Unggah file data survei Anda dalam format **CSV** atau **XLSX** untuk memulai analisis.")

# ── Upload widget ──────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader(
    "Pilih file data survei (CSV atau XLSX)",
    type=["csv", "xlsx", "xls"],
    help="Baris pertama = nama kolom/pertanyaan. Baris berikutnya = jawaban responden (angka).",
)

st.info("📌 Pastikan baris pertama adalah nama kolom, dan setiap baris berikutnya adalah jawaban satu responden.")

# ── Contoh data ────────────────────────────────────────────────────────────────
with st.expander("💡 Tidak punya data? Gunakan data contoh"):
    if st.button("📋 Muat Data Contoh (120 responden, 15 item, skala 1–4)"):
        import numpy as np
        np.random.seed(42)
        n = 120
        base = [np.random.normal(v, 0.6, n) for v in [3.2, 2.8, 3.0, 2.5, 3.1,
                                                        2.9, 3.3, 2.7, 3.0, 2.8,
                                                        3.1, 2.6, 3.2, 2.9, 3.0]]
        sample = pd.DataFrame({
            f"Q{i+1}": np.clip(np.round(base[i] + np.random.normal(0, 0.3, n)), 1, 4).astype(int)
            for i in range(15)
        })
        st.session_state["df"]           = sample
        st.session_state["filename"]     = "data_contoh.csv"
        likert_cols                      = detect_likert_items(sample)
        st.session_state["likert_cols"]  = likert_cols
        smin, smax                       = get_likert_scale_range(sample, likert_cols)
        st.session_state["scale_min"]    = int(smin)
        st.session_state["scale_max"]    = int(smax)
        st.session_state["reverse_cols"] = []
        st.success(f"✅ Data contoh dimuat! {n} responden, 15 pertanyaan, skala 1–4.")

# ── Proses file yang diupload ──────────────────────────────────────────────────
if uploaded_file is not None:
    df = load_data(uploaded_file)
    if df is not None:
        st.session_state["df"]           = df
        st.session_state["filename"]     = uploaded_file.name
        likert_cols                      = detect_likert_items(df)
        st.session_state["likert_cols"]  = likert_cols
        smin, smax                       = get_likert_scale_range(df, likert_cols)
        st.session_state["scale_min"]    = int(smin)
        st.session_state["scale_max"]    = int(smax)
        st.session_state["reverse_cols"] = []
        st.success(f"✅ File **{uploaded_file.name}** berhasil diunggah!")

# ── Tampilkan data ─────────────────────────────────────────────────────────────
if "df" in st.session_state and st.session_state["df"] is not None:
    df          = st.session_state["df"]
    summary     = get_data_summary(df)
    likert_cols = st.session_state.get("likert_cols", [])
    scale_min   = st.session_state.get("scale_min", 1)
    scale_max   = st.session_state.get("scale_max", 4)

    # ── Ringkasan metrik ───────────────────────────────────────────────────────
    st.markdown("### 📊 Ringkasan Dataset")
    missing_pct = round(summary['missing_total'] / max(df.shape[0] * df.shape[1], 1) * 100, 1)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Jumlah Responden",        summary['jumlah_responden'])
    c2.metric("Jumlah Kolom",            summary['jumlah_kolom'])
    c3.metric("Item Likert Terdeteksi",  len(likert_cols))
    c4.metric("Data Kosong (%)",         f"{missing_pct}%")

    # ── Preview data ───────────────────────────────────────────────────────────
    st.markdown("### 🔍 Pratinjau Dataset (10 Baris Pertama)")
    st.dataframe(df.head(10,
        hide_index=True,
    ), use_container_width=True, height=260)

    # ── Missing values ─────────────────────────────────────────────────────────
    st.markdown("### ❓ Ringkasan Nilai Kosong")
    missing_df = summary["missing_per_kolom"][summary["missing_per_kolom"] > 0]
    if len(missing_df) == 0:
        st.success("✅ Tidak ada nilai kosong. Data siap dianalisis!")
    else:
        st.warning(f"⚠️ Ditemukan nilai kosong pada {len(missing_df)} kolom:")
        tbl = pd.DataFrame({
            "Kolom": missing_df.index,
            "Jumlah Kosong": missing_df.values,
            "Persentase (%)": (missing_df.values / len(df) * 100).round(2),
        })
        st.dataframe(tbl, use_container_width=True, hide_index=True)

    # ── Deteksi Likert ─────────────────────────────────────────────────────────
    st.markdown("### 📋 Deteksi Item Likert")
    if likert_cols:
        st.success(f"✅ Terdeteksi **{len(likert_cols)} item Likert** dengan skala **{scale_min}–{scale_max}**.")
        st.write("Item yang terdeteksi:", ", ".join([f"`{c}`" for c in likert_cols]))
    else:
        st.warning("⚠️ Tidak ada item Likert terdeteksi. Pastikan kolom numerik dengan nilai 1–7.")

    # ── Konfirmasi pilihan ─────────────────────────────────────────────────────
    st.markdown("#### ✏️ Konfirmasi atau Ubah Item Likert")
    numeric_cols    = get_numeric_columns(df)
    confirmed_cols  = st.multiselect(
        "Pilih kolom yang akan dianalisis sebagai item Likert:",
        options=numeric_cols,
        default=likert_cols,
    )
    if st.button("💾 Simpan Pilihan Item"):
        st.session_state["likert_cols"] = confirmed_cols
        smin, smax = get_likert_scale_range(df, confirmed_cols)
        st.session_state["scale_min"]   = int(smin)
        st.session_state["scale_max"]   = int(smax)
        st.success(f"✅ {len(confirmed_cols)} item tersimpan. Skala: {smin}–{smax}.")

    # ── Info kolom ─────────────────────────────────────────────────────────────
    st.markdown("### 🔢 Informasi Kolom")
    col_info = pd.DataFrame({
        "Kolom":       df.columns,
        "Tipe Data":   df.dtypes.astype(str).values,
        "Nilai Unik":  [df[c].nunique() for c in df.columns],
        "Min":         [df[c].min() if pd.api.types.is_numeric_dtype(df[c]) else "-" for c in df.columns],
        "Max":         [df[c].max() if pd.api.types.is_numeric_dtype(df[c]) else "-" for c in df.columns],
        "Missing":     [df[c].isnull().sum() for c in df.columns],
    })
    st.dataframe(col_info, use_container_width=True, hide_index=True)

else:
    st.info("👆 Silakan unggah file atau muat data contoh untuk memulai.")
