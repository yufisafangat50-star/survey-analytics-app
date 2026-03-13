"""
3_Uji_Validitas.py - Uji validitas item menggunakan Corrected Item-Total Correlation
"""
import streamlit as st
import pandas as pd
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules.validity_test import corrected_item_total_correlation, get_validity_summary
from modules.reverse_items import apply_reverse_items
from modules.visualizations import plot_validity_barchart, make_short_labels
from modules.interpretation import validity_interpretation

st.set_page_config(page_title="Uji Validitas", page_icon="✅", layout="wide")

# ── Helper interpretasi gabungan (inline agar tidak bergantung versi modul) ────
def combined_label(r, p, threshold=0.30, alpha=0.05):
    valid = r > threshold
    sig   = p < alpha
    if valid and sig:
        return ("✅ Valid & Signifikan",
                "Pertanyaan ini mengukur hal yang sama dengan kuesioner secara "
                "keseluruhan, dan hasilnya dapat dipercaya.")
    elif valid and not sig:
        return ("⚠️ Valid tapi Belum Meyakinkan",
                "Pertanyaan cukup relevan, namun butuh lebih banyak responden "
                "untuk memastikan hasilnya.")
    elif not valid and sig:
        return ("ℹ️ Kurang Relevan",
                "Pertanyaan kurang mencerminkan topik kuesioner, meskipun "
                "polanya konsisten di semua responden.")
    else:
        return ("❌ Tidak Valid",
                "Pertanyaan tidak mencerminkan topik kuesioner dan hasilnya "
                "tidak dapat diandalkan.")


st.title("✅ Uji Validitas Kuesioner")
st.markdown("Uji apakah setiap pertanyaan benar-benar mengukur hal yang ingin diukur.")

with st.expander("📚 Apa itu Uji Validitas? Baca di sini dulu!"):
    st.markdown("""
    **Uji Validitas** mengukur apakah setiap pertanyaan dalam kuesioner benar-benar
    mencerminkan topik yang ingin diukur.

    **Metode:** *Corrected Item-Total Correlation (CITC)*
    — setiap pertanyaan dibandingkan korelasinya dengan total skor semua pertanyaan **lainnya**.

    ---
    ### 📊 Dua Angka Penting

    | Angka | Artinya |
    |-------|---------|
    | **r (Korelasi)** | Seberapa kuat pertanyaan ini berkaitan dengan keseluruhan kuesioner. Minimal **r > 0.30** |
    | **p-value** | Seberapa yakin kita bahwa hubungan itu bukan kebetulan. Umumnya **p < 0.05** |

    ---
    ### 🏷️ Empat Kategori Hasil

    | Hasil | Artinya |
    |-------|---------|
    | ✅ **Valid & Signifikan** | Pertanyaan mengukur hal yang sama dan hasilnya dapat dipercaya |
    | ⚠️ **Valid tapi Belum Meyakinkan** | Cukup relevan, tapi butuh lebih banyak responden |
    | ℹ️ **Kurang Relevan** | Polanya konsisten, namun korelasinya terlalu lemah dengan topik utama |
    | ❌ **Tidak Valid** | Tidak mencerminkan topik kuesioner dan tidak dapat diandalkan |
    """)

# ── Check session ──────────────────────────────────────────────────────────────
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
    st.caption("Standar umum: r > 0.30. Beberapa peneliti menggunakan r > 0.25 untuk sampel kecil.")

# ── Jalankan uji ───────────────────────────────────────────────────────────────
if st.button("🔬 Jalankan Uji Validitas", type="primary"):
    with st.spinner("Menghitung..."):
        validity_df = corrected_item_total_correlation(df_analysis, likert_cols, threshold)
        st.session_state["validity_df"]        = validity_df
        st.session_state["validity_threshold"] = threshold

if "validity_df" not in st.session_state:
    st.stop()

validity_df = st.session_state["validity_df"].copy()

# Recalculate jika threshold berubah
validity_df["Status"] = validity_df["Korelasi Item-Total"].apply(
    lambda r: "Valid ✅" if r > threshold else "Tidak Valid ❌"
)
interp_cols = validity_df.apply(
    lambda row: pd.Series(combined_label(
        row["Korelasi Item-Total"], row["p-value"], threshold
    ), index=["Interpretasi", "Penjelasan"]),
    axis=1
)
validity_df["Interpretasi"] = interp_cols["Interpretasi"]
validity_df["Penjelasan"]   = interp_cols["Penjelasan"]

valid_count, invalid_count = get_validity_summary(validity_df)
total = len(validity_df)

# ── Ringkasan metrik ───────────────────────────────────────────────────────────
n_valid_sig  = ((validity_df["Korelasi Item-Total"] >  threshold) & (validity_df["p-value"] < 0.05)).sum()
n_valid_nsig = ((validity_df["Korelasi Item-Total"] >  threshold) & (validity_df["p-value"] >= 0.05)).sum()
n_inv_sig    = ((validity_df["Korelasi Item-Total"] <= threshold) & (validity_df["p-value"] < 0.05)).sum()
n_inv_nsig   = ((validity_df["Korelasi Item-Total"] <= threshold) & (validity_df["p-value"] >= 0.05)).sum()

c1, c2, c3, c4 = st.columns(4)
c1.metric("✅ Valid & Signifikan",          n_valid_sig)
c2.metric("⚠️ Valid tapi Belum Meyakinkan", n_valid_nsig)
c3.metric("ℹ️ Kurang Relevan",              n_inv_sig)
c4.metric("❌ Tidak Valid",                  n_inv_nsig)

summary_msg = validity_interpretation(valid_count, total)
if valid_count == total:       st.success(summary_msg)
elif valid_count >= total*0.7: st.warning(summary_msg)
else:                          st.error(summary_msg)

# ── Grafik ─────────────────────────────────────────────────────────────────────
st.markdown("### 📊 Grafik Korelasi Item-Total")
st.caption(
    "Hijau = Valid (r > 0.30). Merah = Tidak Valid. "
    "Garis putus-putus = batas validitas. "
    "Arahkan kursor ke batang untuk melihat pertanyaan lengkap."
)
st.plotly_chart(plot_validity_barchart(validity_df), use_container_width=True)

short_map, legend_df = make_short_labels(likert_cols)
if any(short_map[c] != c for c in likert_cols):
    with st.expander("📖 Keterangan kode pertanyaan di grafik"):
        st.dataframe(legend_df, use_container_width=True, hide_index=True)

# ── Tabel lengkap ──────────────────────────────────────────────────────────────
st.markdown("### 📋 Tabel Hasil Uji Validitas")
st.caption("Kolom **Penjelasan** mendeskripsikan arti hasil untuk setiap pertanyaan.")

display_df = validity_df.copy()

# Nomor urut mulai dari 1 (bukan 0)
display_df.insert(0, "No",   range(1, len(display_df) + 1))
display_df.insert(1, "Kode", [short_map.get(c, c) for c in display_df["Item"]])
display_df["Item"] = display_df["Item"].apply(
    lambda x: x[:55] + "…" if len(x) > 55 else x
)

cols_show  = ["No", "Kode", "Item", "Korelasi Item-Total", "p-value", "Interpretasi", "Penjelasan"]
display_df = display_df[cols_show]

def color_row(row):
    interp = row["Interpretasi"]
    if "Valid & Signifikan"   in interp: bg = "background-color:#d4edda;"
    elif "Belum Meyakinkan"   in interp: bg = "background-color:#fff3cd;"
    elif "Kurang Relevan"     in interp: bg = "background-color:#d1ecf1;"
    else:                                bg = "background-color:#f8d7da;"
    return [bg] * len(row)

st.dataframe(
    display_df.style.apply(color_row, axis=1),
    use_container_width=True,
    hide_index=True,
    height=min(700, 65 + 35 * len(display_df)),
)
st.markdown(
    "<small>🟩 Hijau = Valid & Signifikan &nbsp;|&nbsp; "
    "🟨 Kuning = Valid tapi Belum Meyakinkan &nbsp;|&nbsp; "
    "🟦 Biru = Kurang Relevan &nbsp;|&nbsp; "
    "🟥 Merah = Tidak Valid</small>",
    unsafe_allow_html=True,
)

# ── Rekomendasi ────────────────────────────────────────────────────────────────
if invalid_count > 0 or n_inv_sig > 0:
    st.markdown("### 💡 Rekomendasi")
    if invalid_count > 0:
        gugur      = validity_df[validity_df["Status"] == "Tidak Valid ❌"]["Item"].tolist()
        gugur_kode = [short_map.get(x, x) for x in gugur]
        st.warning(
            f"**{invalid_count} pertanyaan perlu ditinjau ulang:** {', '.join(gugur_kode)}\n\n"
            "Kemungkinan penyebab: pertanyaan ambigu, tidak relevan dengan topik utama, "
            "atau salah pengelompokan antara pertanyaan positif dan negatif."
        )
    if n_inv_sig > 0:
        kurang = validity_df[
            (validity_df["Korelasi Item-Total"] <= threshold) &
            (validity_df["p-value"] < 0.05)
        ]["Item"].tolist()
        kurang_kode = [short_map.get(x, x) for x in kurang]
        st.info(
            f"**{n_inv_sig} pertanyaan berkategori 'Kurang Relevan':** {', '.join(kurang_kode)}\n\n"
            "Pertanyaan ini memiliki pola yang konsisten di semua responden, namun "
            "korelasinya dengan topik utama masih terlalu lemah. "
            "Pertimbangkan untuk memperjelas redaksi pertanyaannya."
        )

# ── Download ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.download_button(
    "⬇️ Unduh Hasil Uji Validitas (CSV)",
    validity_df.to_csv(index=False).encode("utf-8"),
    "hasil_validitas.csv", "text/csv",
)
