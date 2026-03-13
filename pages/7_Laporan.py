"""
7_Laporan.py - Generate and download analysis report in Excel format
"""
import streamlit as st
import pandas as pd
import io, sys, os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules.reverse_items import apply_reverse_items
from modules.reliability_test import cronbach_alpha, alpha_if_item_deleted, interpret_alpha
from modules.validity_test import corrected_item_total_correlation
from modules.likert_detection import interpret_score

st.set_page_config(page_title="Laporan", page_icon="📥", layout="wide")

st.title("📥 Generate Laporan Analisis")
st.markdown("Unduh laporan lengkap hasil analisis survei dalam format **Excel**.")

# ── Check session ──────────────────────────────────────────────────────────────
if "df" not in st.session_state or st.session_state["df"] is None:
    st.warning("⚠️ Belum ada data. Silakan upload di halaman **Upload Data** terlebih dahulu.")
    st.stop()

df           = st.session_state["df"]
likert_cols  = st.session_state.get("likert_cols", [])
scale_min    = st.session_state.get("scale_min", 1)
scale_max    = st.session_state.get("scale_max", 4)
reverse_cols = st.session_state.get("reverse_cols", [])
filename     = st.session_state.get("filename", "data_survei")

if not likert_cols:
    st.warning("⚠️ Tidak ada item Likert yang dikonfirmasi.")
    st.stop()

df_analysis = apply_reverse_items(df, likert_cols, reverse_cols, scale_min, scale_max)

# ── Report Options ─────────────────────────────────────────────────────────────
st.markdown("### ⚙️ Pilih Konten Laporan")
c1, c2 = st.columns(2)
with c1:
    include_validity    = st.checkbox("✅ Uji Validitas",    value=True)
    include_reliability = st.checkbox("🔁 Uji Reliabilitas", value=True)
with c2:
    include_efa     = st.checkbox("🧩 Analisis Faktor",             value=("efa_loadings" in st.session_state))
    include_insight = st.checkbox("📊 Statistik Deskriptif & Insight", value=True)

report_title = st.text_input("Judul Laporan:", value="Laporan Analisis Kuesioner Survei")
org_name     = st.text_input("Nama Organisasi/Peneliti:", value="")

# ── Preview ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📋 Pratinjau Laporan")

# Ringkasan
st.markdown("#### 📊 Ringkasan Data")
c1, c2, c3 = st.columns(3)
c1.metric("Jumlah Responden",  len(df))
c2.metric("Jumlah Item Likert", len(likert_cols))
c3.metric("Skala Digunakan",   f"{scale_min} – {scale_max}")

# Validitas preview
if include_validity:
    st.markdown("#### ✅ Uji Validitas")
    if "validity_df" in st.session_state:
        vdf     = st.session_state["validity_df"]
        v_count = (vdf["Status"] == "Valid ✅").sum()
        st.write(f"Valid: **{v_count}** / {len(vdf)} item")
        st.dataframe(vdf, use_container_width=True, height=200, hide_index=True)
    else:
        st.info("ℹ️ Jalankan Uji Validitas terlebih dahulu untuk menyertakannya dalam laporan.")

# Reliabilitas preview
if include_reliability:
    st.markdown("#### 🔁 Uji Reliabilitas")
    # Safe get: check key existence explicitly to avoid DataFrame bool ambiguity
    if "cronbach_alpha" in st.session_state:
        alpha_val = st.session_state["cronbach_alpha"]
    else:
        alpha_val = cronbach_alpha(df_analysis, likert_cols)
    st.write(f"Cronbach Alpha: **{alpha_val}** — {interpret_alpha(alpha_val)}")

# EFA preview
if include_efa:
    st.markdown("#### 🧩 Analisis Faktor")
    if "efa_loadings" in st.session_state:
        st.dataframe(
            st.session_state["efa_loadings"].round(3),
            use_container_width=True,
            height=200,
            hide_index=True,
        )
    else:
        st.info("ℹ️ Jalankan Analisis Faktor terlebih dahulu untuk menyertakannya.")

# ── Generate Excel ─────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📥 Unduh Laporan")

if st.button("📊 Generate Laporan Excel", type="primary"):
    with st.spinner("Membuat laporan Excel..."):
        output = io.BytesIO()
        try:
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                wb = writer.book

                # Formats
                title_fmt = wb.add_format({
                    "bold": True, "font_size": 14,
                    "bg_color": "#1a73e8", "font_color": "white",
                    "align": "center", "valign": "vcenter", "border": 1,
                })
                header_fmt = wb.add_format({
                    "bold": True, "bg_color": "#e8f0fe", "border": 1, "align": "center"
                })
                cell_fmt = wb.add_format({"border": 1})

                # Sheet 1: Ringkasan
                ws = wb.add_worksheet("Ringkasan")
                ws.set_column("A:A", 35)
                ws.set_column("B:B", 30)
                ws.merge_range("A1:B1", report_title, title_fmt)
                ws.set_row(0, 30)

                rows = [
                    ["Organisasi/Peneliti",      org_name or "-"],
                    ["Tanggal Laporan",           datetime.now().strftime("%d %B %Y %H:%M")],
                    ["Nama File Data",            filename],
                    ["Jumlah Responden",          len(df)],
                    ["Jumlah Item Likert",         len(likert_cols)],
                    ["Skala Likert",              f"{scale_min} – {scale_max}"],
                    ["Item Negatif (Reversed)",   len(reverse_cols)],
                    ["Rata-rata Skor Keseluruhan", round(df_analysis[likert_cols].mean().mean(), 4)],
                ]
                for i, (lbl, val) in enumerate(rows, start=1):
                    ws.write(i, 0, lbl, header_fmt)
                    ws.write(i, 1, val, cell_fmt)

                # Sheet 2: Data Asli
                df[likert_cols].to_excel(writer, sheet_name="Data Asli", index=False)

                # Sheet 3: Data Setelah Reverse
                df_analysis.to_excel(writer, sheet_name="Data Setelah Reverse", index=False)

                # Sheet 4: Statistik Deskriptif
                if include_insight:
                    desc = df_analysis[likert_cols].describe().T.round(4)
                    desc.index.name = "Item"
                    means = df_analysis[likert_cols].mean().round(3)
                    desc["Interpretasi"] = [interpret_score(m, scale_min, scale_max) for m in means]
                    desc.to_excel(writer, sheet_name="Statistik Deskriptif")

                # Sheet 5: Uji Validitas
                if include_validity:
                    if "validity_df" in st.session_state:
                        vdf = st.session_state["validity_df"]
                    else:
                        vdf = corrected_item_total_correlation(df_analysis, likert_cols)
                    vdf.to_excel(writer, sheet_name="Uji Validitas", index=False)

                # Sheet 6: Uji Reliabilitas
                if include_reliability:
                    # Use explicit key check — never use 'or' on a DataFrame
                    if "cronbach_alpha" in st.session_state:
                        alpha_val = st.session_state["cronbach_alpha"]
                    else:
                        alpha_val = cronbach_alpha(df_analysis, likert_cols)

                    if "alpha_deleted_df" in st.session_state:
                        alpha_del_df = st.session_state["alpha_deleted_df"]
                    else:
                        alpha_del_df = alpha_if_item_deleted(df_analysis, likert_cols)

                    rel_summary = pd.DataFrame([
                        {"Statistik": "Cronbach Alpha (α)", "Nilai": alpha_val},
                        {"Statistik": "Interpretasi",       "Nilai": interpret_alpha(alpha_val)},
                        {"Statistik": "Jumlah Item",        "Nilai": len(likert_cols)},
                    ])
                    rel_summary.to_excel(writer, sheet_name="Uji Reliabilitas",
                                         index=False, startrow=0)
                    alpha_del_df.to_excel(writer, sheet_name="Uji Reliabilitas",
                                          index=False, startrow=5)

                # Sheet 7: Analisis Faktor
                if include_efa and "efa_loadings" in st.session_state:
                    st.session_state["efa_loadings"].round(4).to_excel(
                        writer, sheet_name="Analisis Faktor"
                    )
                    if "efa_variance" in st.session_state:
                        st.session_state["efa_variance"].round(4).to_excel(
                            writer, sheet_name="Varians Faktor"
                        )

            output.seek(0)
            st.success("✅ Laporan Excel berhasil dibuat!")
            fname = f"laporan_survei_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
            st.download_button(
                label="⬇️ Unduh Laporan Excel",
                data=output.getvalue(),
                file_name=fname,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        except Exception as e:
            st.error(f"❌ Gagal membuat laporan: {e}")
            st.exception(e)

# ── Download per bagian ────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📂 Unduh Per Bagian (CSV)")
c1, c2, c3 = st.columns(3)

with c1:
    if "validity_df" in st.session_state:
        st.download_button(
            "⬇️ Hasil Validitas",
            st.session_state["validity_df"].to_csv(index=False).encode("utf-8"),
            "validitas.csv", "text/csv"
        )
    else:
        st.caption("Jalankan Uji Validitas dulu")

with c2:
    if "alpha_deleted_df" in st.session_state:
        st.download_button(
            "⬇️ Hasil Reliabilitas",
            st.session_state["alpha_deleted_df"].to_csv(index=False).encode("utf-8"),
            "reliabilitas.csv", "text/csv"
        )
    else:
        st.caption("Jalankan Uji Reliabilitas dulu")

with c3:
    if "efa_loadings" in st.session_state:
        st.download_button(
            "⬇️ Factor Loading",
            st.session_state["efa_loadings"].round(4).to_csv().encode("utf-8"),
            "factor_loading.csv", "text/csv"
        )
    else:
        st.caption("Jalankan Analisis Faktor dulu")
