"""
5_Analisis_Faktor.py - Analisis Faktor Eksploratori (EFA)
"""
import streamlit as st
import pandas as pd
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules.efa_analysis import (
    run_kmo_bartlett, interpret_kmo, run_efa,
    get_factor_assignments, FACTOR_ANALYZER_AVAILABLE
)
from modules.reverse_items import apply_reverse_items
from modules.visualizations import plot_scree, plot_factor_loadings_heatmap, make_label_legend, make_short_labels
from modules.interpretation import kmo_interpretation, bartlett_interpretation, efa_factor_interpretation

st.set_page_config(page_title="Analisis Faktor", page_icon="🧩", layout="wide")

st.title("🧩 Analisis Faktor Eksploratori (EFA)")
st.markdown("Temukan struktur tersembunyi dalam data kuesioner Anda.")

with st.expander("📚 Apa itu Analisis Faktor? Baca di sini dulu!"):
    st.markdown("""
    ### 🧩 Analisis Faktor — Penjelasan Sederhana

    Bayangkan Anda punya 15 pertanyaan survei. Analisis Faktor secara otomatis
    **mengelompokkan pertanyaan-pertanyaan yang saling berkaitan** ke dalam satu kelompok
    yang disebut **faktor** (atau konstruk).

    **Contoh:** Jika Q1, Q2, Q3 semuanya bertanya tentang "kualitas pelayanan",
    maka analisis faktor akan otomatis memasukkan ketiganya ke dalam satu faktor yang sama.
    Anda kemudian memberi nama faktor tersebut, misalnya **"Kualitas Pelayanan"**.

    ---
    ### 📊 Cara Membaca Tabel Factor Loading

    | Nilai Loading | Artinya |
    |---------------|---------|
    | ≥ 0.70 | 🟩 Sangat kuat — pertanyaan sangat mewakili faktor ini |
    | 0.40–0.69 | 🟨 Signifikan — pertanyaan cukup mewakili faktor ini |
    | < 0.40 | Lemah — pertanyaan kurang mewakili faktor manapun |

    Lihat nilai terbesar (hijau) di setiap baris — itulah faktor tempat pertanyaan tersebut masuk.

    ---
    ### 🏷️ Nama Faktor
    Faktor **tidak punya nama otomatis**. Anda perlu memberi nama sendiri
    berdasarkan pertanyaan apa saja yang masuk ke dalamnya.
    """)

if "df" not in st.session_state or st.session_state["df"] is None:
    st.warning("⚠️ Belum ada data. Silakan upload di halaman **Upload Data**.")
    st.stop()

df           = st.session_state["df"]
likert_cols  = st.session_state.get("likert_cols", [])
scale_min    = st.session_state.get("scale_min", 1)
scale_max    = st.session_state.get("scale_max", 4)
reverse_cols = st.session_state.get("reverse_cols", [])

if len(likert_cols) < 3:
    st.warning("⚠️ Dibutuhkan minimal 3 item Likert untuk Analisis Faktor.")
    st.stop()

df_analysis = apply_reverse_items(df, likert_cols, reverse_cols, scale_min, scale_max)
df_clean    = df_analysis.dropna()
n_missing   = len(df_analysis) - len(df_clean)
if n_missing > 0:
    st.warning(f"⚠️ {n_missing} baris dihapus karena nilai kosong. Menggunakan {len(df_clean)} baris.")

# Buat label pendek sekali di awal — dipakai konsisten di semua tabel & chart
short_map, label_legend = make_short_labels(likert_cols)
use_short = any(short_map[c] != c for c in likert_cols)  # True jika ada penyingkatan

# ── Settings ───────────────────────────────────────────────────────────────────
with st.expander("⚙️ Pengaturan Analisis Faktor"):
    c1, c2 = st.columns(2)
    with c1:
        auto_factors    = st.checkbox("Tentukan jumlah faktor otomatis (eigenvalue > 1)", value=True)
        n_factors_input = None
        if not auto_factors:
            n_factors_input = st.number_input("Jumlah faktor:", min_value=1,
                                               max_value=len(likert_cols)-1, value=3)
    with c2:
        rotation          = st.selectbox("Metode rotasi:", ["varimax","promax","oblimin","quartimax"])
        loading_threshold = st.slider("Batas loading signifikan:", 0.20, 0.70, 0.40, 0.05)

# ── Langkah 1: KMO & Bartlett ──────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🔬 Langkah 1: Apakah Data Cocok untuk Analisis Faktor?")

if st.button("▶️ Jalankan Uji KMO & Bartlett", type="primary"):
    with st.spinner("Menghitung..."):
        kmo, chi_sq, p_val, _ = run_kmo_bartlett(df_clean, likert_cols)
        if kmo is not None:
            st.session_state["kmo"]          = kmo
            st.session_state["bartlett_chi"] = chi_sq
            st.session_state["bartlett_p"]   = p_val

if "kmo" in st.session_state:
    kmo    = st.session_state["kmo"]
    chi_sq = st.session_state["bartlett_chi"]
    p_val  = st.session_state["bartlett_p"]
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown("**Uji KMO**")
            st.markdown(f"Nilai KMO: `{round(kmo, 4)}`  \nKategori: **{interpret_kmo(kmo)}**")
            st.markdown(kmo_interpretation(kmo))
            st.caption("KMO ≥ 0.50 = layak. Semakin tinggi semakin baik.")
    with c2:
        with st.container(border=True):
            st.markdown("**Uji Bartlett**")
            st.markdown(f"Chi-Square: `{round(chi_sq,4)}`  \np-value: `{round(p_val,6)}`")
            st.markdown(bartlett_interpretation(p_val))
            st.caption("p < 0.05 = ada korelasi antar item, cocok untuk EFA.")
    if kmo < 0.50 or p_val >= 0.05:
        st.error("❌ Syarat EFA tidak terpenuhi.")
    else:
        st.success("✅ Data layak untuk dilanjutkan ke Analisis Faktor!")

# ── Langkah 2: EFA ────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🔬 Langkah 2: Ekstraksi & Pengelompokan Faktor")

if st.button("▶️ Jalankan Analisis Faktor", type="primary"):
    with st.spinner("Menjalankan..."):
        try:
            loadings_df, eigenvalues, variance_df, n_factors_found = run_efa(
                df_clean, likert_cols, n_factors_input, rotation
            )
            if loadings_df is not None:
                st.session_state["efa_loadings"]    = loadings_df
                st.session_state["efa_eigenvalues"] = eigenvalues
                st.session_state["efa_variance"]    = variance_df
                st.session_state["efa_n_factors"]   = n_factors_found
                st.session_state["factor_names"]    = {
                    f"Faktor {i+1}": f"Faktor {i+1}" for i in range(n_factors_found)
                }
                st.success(f"✅ Selesai! Ditemukan **{n_factors_found} faktor**.")
        except Exception as e:
            st.error(f"❌ Gagal: {e}")
            st.exception(e)

if "efa_loadings" not in st.session_state:
    st.stop()

loadings_df     = st.session_state["efa_loadings"]
eigenvalues     = st.session_state["efa_eigenvalues"]
variance_df     = st.session_state["efa_variance"]
n_factors_found = st.session_state["efa_n_factors"]
factor_names    = st.session_state.get("factor_names", {
    f"Faktor {i+1}": f"Faktor {i+1}" for i in range(n_factors_found)
})

st.info(efa_factor_interpretation(n_factors_found))

# ── Beri Nama Faktor ──────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🏷️ Langkah 3: Beri Nama pada Setiap Faktor")
st.caption("Lihat pengelompokan pertanyaan di bawah, lalu beri nama yang bermakna untuk setiap faktor.")

name_cols = st.columns(min(4, n_factors_found))
for i in range(n_factors_found):
    key = f"Faktor {i+1}"
    with name_cols[i % len(name_cols)]:
        new_name = st.text_input(
            f"Nama Faktor {i+1}:",
            value=factor_names.get(key, key),
            key=f"fname_{i}",
            placeholder="Contoh: Kepuasan Layanan"
        )
        factor_names[key] = new_name
st.session_state["factor_names"] = factor_names

# ── Pengelompokan per Faktor ───────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📦 Langkah 4: Hasil Pengelompokan Pertanyaan")
st.caption(f"Setiap pertanyaan dimasukkan ke faktor dengan loading tertinggi (≥ {loading_threshold}).")

assignments   = get_factor_assignments(loadings_df, loading_threshold)
factor_groups = {}
unassigned    = []
for item, (factor, loading) in assignments.items():
    if factor == "Tidak ada":
        unassigned.append(item)
    else:
        factor_groups.setdefault(factor, []).append((item, loading))

n_cols = min(3, max(1, len(factor_groups)))
cols   = st.columns(n_cols)
for i, (fkey, items) in enumerate(factor_groups.items()):
    display_name = factor_names.get(fkey, fkey)
    with cols[i % n_cols]:
        with st.container(border=True):
            st.markdown(f"#### {fkey}")
            if display_name != fkey:
                st.markdown(f"*📌 {display_name}*")
            st.markdown(f"**{len(items)} pertanyaan:**")
            for item, loading in sorted(items, key=lambda x: abs(x[1]), reverse=True):
                short_lbl = short_map.get(item, item)
                icon      = "🟩" if abs(loading) >= 0.60 else "🟨"
                # Tampilkan kode pendek + nama panjang jika berbeda
                if short_lbl != item:
                    st.markdown(f"{icon} **{short_lbl}** — loading: **{loading:+.3f}**")
                    st.caption(f"   ↳ {item}")
                else:
                    st.markdown(f"{icon} `{item}` — loading: **{loading:+.3f}**")

if unassigned:
    short_unassigned = [short_map.get(x, x) for x in unassigned]
    st.warning(
        f"⚠️ **{len(unassigned)} pertanyaan tidak masuk faktor manapun** "
        f"(loading < {loading_threshold}): {', '.join(short_unassigned)}"
    )

# ── Tabel Factor Loading Lengkap ──────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📋 Tabel Factor Loading Lengkap")
st.caption(
    "Setiap baris = satu pertanyaan. Setiap kolom = satu faktor. "
    "Hijau = loading signifikan. Kolom pertama menunjukkan faktor dominan."
)

# Buat display_df dengan index = kode pendek (UNIK, tidak rename kolom faktor)
display_df = loadings_df.copy()
display_df.index = [short_map.get(c, c) for c in loadings_df.index]

# Tambah kolom Faktor Dominan & Nama Konstruk
dominan_col      = []
nama_dominan_col = []
for item in loadings_df.index:
    row     = loadings_df.loc[item]
    max_val = row.abs().max()
    if max_val >= loading_threshold:
        fkey = row.abs().idxmax()
        dominan_col.append(f"{fkey} ({row[fkey]:+.3f})")
        nama_dominan_col.append(factor_names.get(fkey, fkey))
    else:
        dominan_col.append("— (loading lemah)")
        nama_dominan_col.append("—")

display_df.insert(0, "Faktor Dominan", dominan_col)
display_df.insert(1, "Nama Konstruk",  nama_dominan_col)

# Highlighter — hanya pada kolom numerik (bukan 2 kolom teks di awal)
numeric_cols = [c for c in display_df.columns if c not in ("Faktor Dominan", "Nama Konstruk")]

def highlight_loading(val):
    try:
        f = float(val)
        if abs(f) >= 0.60: return "background-color:#a9dfbf;font-weight:bold;"
        if abs(f) >= loading_threshold: return "background-color:#d5f5e3;font-weight:bold;"
    except Exception:
        pass
    return ""

st.dataframe(
    display_df.round(3).style.applymap(highlight_loading, subset=numeric_cols),
    use_container_width=True,
    height=min(600, 65 + 35 * len(display_df)),
    hide_index=True,
)
st.caption("🟩 Hijau tua ≥ 0.60 (sangat kuat).  🟩 Hijau muda ≥ 0.40 (signifikan).")

# ── Legenda Kode ──────────────────────────────────────────────────────────────
if use_short:
    st.markdown("---")
    st.markdown("### 📖 Keterangan Kode Pertanyaan")
    st.caption("Kode pendek digunakan di semua grafik dan tabel agar lebih mudah dibaca.")
    # Tambah kolom Faktor Dominan ke legenda
    legend_df = label_legend.copy()
    legend_df["Faktor Dominan"] = [
        factor_names.get(assignments.get(c, ("—",None))[0], assignments.get(c, ("—",None))[0])
        if assignments.get(c, ("Tidak ada",None))[0] != "Tidak ada"
        else "—"
        for c in likert_cols
    ]
    st.dataframe(legend_df, use_container_width=True, hide_index=True)

# ── Scree Plot ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📉 Scree Plot")
st.caption("Faktor di atas garis merah (eigenvalue > 1) dianggap signifikan. Cari 'siku' pada grafik.")
st.plotly_chart(plot_scree(eigenvalues), use_container_width=True)

# ── Varians ────────────────────────────────────────────────────────────────────
st.markdown("### 📊 Berapa Persen Data yang Dijelaskan?")
st.caption("Kumulatif Varians idealnya ≥ 50%. Semakin tinggi semakin baik.")
vd = variance_df.copy()
vd.index = [
    f"{fk} — {factor_names[fk]}" if factor_names.get(fk, fk) != fk else fk
    for fk in vd.index
]
vd["Proporsi Varians"]  = (vd["Proporsi Varians"]  * 100).round(2).astype(str) + "%"
vd["Kumulatif Varians"] = (vd["Kumulatif Varians"] * 100).round(2).astype(str) + "%"
vd["SS Loadings"]       = vd["SS Loadings"].round(3)
st.dataframe(vd, use_container_width=True,
        hide_index=True,
    )

# ── Heatmap ────────────────────────────────────────────────────────────────────
st.markdown("### 🌡️ Heatmap Factor Loading")
st.caption("Biru = korelasi positif dengan faktor. Merah = negatif. Semakin pekat = semakin kuat.")
# Rename kolom heatmap dengan nama faktor (aman karena hanya kolom, bukan index)
heatmap_df = loadings_df.copy()
heatmap_df.columns = [
    f"{c}\n{factor_names[c]}" if factor_names.get(c, c) != c else c
    for c in heatmap_df.columns
]
st.plotly_chart(plot_factor_loadings_heatmap(heatmap_df), use_container_width=True)

# ── Legenda di bawah heatmap ──────────────────────────────────────────────────
if use_short:
    with st.expander("📖 Lihat keterangan kode pertanyaan"):
        st.dataframe(label_legend, use_container_width=True, hide_index=True)

# ── Download ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.download_button(
    "⬇️ Unduh Tabel Factor Loading (CSV)",
    data=display_df.to_csv().encode("utf-8"),
    file_name="factor_loadings.csv",
    mime="text/csv",
)
