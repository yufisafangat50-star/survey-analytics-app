"""
3_Uji_Validitas.py - Uji validitas item menggunakan Corrected Item-Total Correlation
"""
import streamlit as st
import pandas as pd
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules.validity_test import corrected_item_total_correlation, get_validity_summary
from modules.reverse_items import apply_reverse_items
from modules.visualizations import plot_validity_barchart
from modules.interpretation import validity_interpretation

st.set_page_config(page_title="Uji Validitas", page_icon="✅", layout="wide")

st.title("✅ Uji Validitas Kuesioner")
st.markdown("Uji apakah setiap pertanyaan benar-benar mengukur hal yang ingin diukur.")

with st.expander("📚 Apa itu Uji Validitas?"):
    st.markdown("""
    **Metode:** *Corrected Item-Total Correlation* — setiap pertanyaan dibandingkan dengan
    total skor semua pertanyaan lainnya.

    | Nilai r | Status |
    |---------|--------|
    | r > 0.30 | ✅ Valid |
    | r ≤ 0.30 | ❌ Tidak Valid |

    Pertanyaan tidak valid sebaiknya **diperbaiki atau dihapus** dari kuesioner.
    """)

if "df" not in st.session_state or st.session_state["df"] is None:
    st.warning("⚠️ Belum ada data. Silakan upload di halaman **Upload Data**.")
    st.stop()

df           = st.session_state["df"]
likert_cols  = st.session_state.get("likert_cols", [])
scale_min    = st.session_state.get("scale_min", 1)
scale_max    = st.session_state.get("scale_max", 4)
reverse_cols = st.session_state.get("reverse_cols", [])

if not likert_cols:
    st.warning("⚠️ Tidak ada item Likert. Konfirmasi di halaman Upload Data.")
    st.stop()

df_analysis = apply_reverse_items(df, likert_cols, reverse_cols, scale_min, scale_max)
if reverse_cols:
    st.info(f"🔁 {len(reverse_cols)} pertanyaan negatif telah dibalik skornya.")

with st.expander("⚙️ Pengaturan"):
    threshold = st.slider("Batas minimum korelasi (r):", 0.10, 0.50, 0.30, 0.05)

if st.button("🔬 Jalankan Uji Validitas", type="primary"):
    with st.spinner("Menghitung..."):
        validity_df = corrected_item_total_correlation(df_analysis, likert_cols)
        validity_df["Status"] = validity_df["Korelasi Item-Total"].apply(
            lambda r: "Valid ✅" if r > threshold else "Tidak Valid ❌"
        )
        st.session_state["validity_df"]        = validity_df
        st.session_state["validity_threshold"] = threshold

if "validity_df" in st.session_state:
    validity_df = st.session_state["validity_df"]
    valid_count, invalid_count = get_validity_summary(validity_df)
    total = len(validity_df)

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Item",      total)
    c2.metric("✅ Valid",        valid_count)
    c3.metric("❌ Tidak Valid",  invalid_count)

    interp = validity_interpretation(valid_count, total)
    if valid_count == total:
        st.success(interp)
    elif valid_count >= total * 0.7:
        st.warning(interp)
    else:
        st.error(interp)

    st.markdown("### 📊 Grafik Korelasi Item-Total")
    st.caption("Hijau = Valid (r > 0.30). Merah = Tidak Valid. Garis putus-putus = batas validitas.")
    st.plotly_chart(plot_validity_barchart(validity_df), use_container_width=True)

    st.markdown("### 📋 Tabel Hasil Uji Validitas")
    def color_status(val):
        if "Valid ✅" in str(val):   return "background-color:#d4edda;color:#155724;"
        if "Tidak Valid" in str(val): return "background-color:#f8d7da;color:#721c24;"
        return ""
    st.dataframe(
        validity_df.style.applymap(color_status, subset=["Status"]),
        use_container_width=True, hide_index=True
    )

    if invalid_count > 0:
        invalid_items = validity_df[validity_df["Status"] == "Tidak Valid ❌"]["Item"].tolist()
        st.warning(
            f"**Pertanyaan tidak valid:** {', '.join(invalid_items)}\n\n"
            "Kemungkinan penyebab: pertanyaan ambigu, tidak relevan, atau salah klasifikasi positif/negatif."
        )

    st.download_button(
        "⬇️ Unduh Hasil (CSV)",
        validity_df.to_csv(index=False).encode("utf-8"),
        "hasil_validitas.csv", "text/csv"
    )
