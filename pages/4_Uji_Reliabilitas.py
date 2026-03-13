"""
4_Uji_Reliabilitas.py - Uji reliabilitas menggunakan Cronbach Alpha
"""
import streamlit as st
import plotly.graph_objects as go
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from modules.reliability_test import (
    cronbach_alpha, alpha_if_item_deleted, interpret_alpha, interpret_alpha_color
)
from modules.reverse_items import apply_reverse_items
from modules.visualizations import plot_alpha_if_deleted, make_label_legend
from modules.interpretation import reliability_interpretation

st.set_page_config(page_title="Uji Reliabilitas", page_icon="🔁", layout="wide")

st.title("🔁 Uji Reliabilitas Kuesioner")
st.markdown("Uji seberapa konsisten kuesioner Anda dalam mengukur hal yang sama.")

with st.expander("📚 Apa itu Cronbach Alpha?"):
    st.markdown("""
    **Cronbach Alpha (α)** mengukur konsistensi internal kuesioner.

    | Nilai Alpha | Interpretasi |
    |-------------|-------------|
    | ≥ 0.90 | 🌟 Sangat Baik |
    | 0.80–0.89 | ✅ Baik |
    | 0.70–0.79 | ⚠️ Cukup |
    | 0.60–0.69 | ⚠️ Kurang |
    | < 0.60 | ❌ Tidak Reliabel |
    """)

if "df" not in st.session_state or st.session_state["df"] is None:
    st.warning("⚠️ Belum ada data. Silakan upload di halaman **Upload Data**.")
    st.stop()

df           = st.session_state["df"]
likert_cols  = st.session_state.get("likert_cols", [])
scale_min    = st.session_state.get("scale_min", 1)
scale_max    = st.session_state.get("scale_max", 4)
reverse_cols = st.session_state.get("reverse_cols", [])

if len(likert_cols) < 2:
    st.warning("⚠️ Dibutuhkan minimal 2 item Likert.")
    st.stop()

df_analysis = apply_reverse_items(df, likert_cols, reverse_cols, scale_min, scale_max)
if reverse_cols:
    st.info(f"🔁 {len(reverse_cols)} pertanyaan negatif telah dibalik.")

with st.expander("⚙️ Pilih Item"):
    selected_items = st.multiselect("Item yang dianalisis:", likert_cols, default=likert_cols)
items_to_use = selected_items if selected_items else likert_cols

if st.button("🔬 Hitung Cronbach Alpha", type="primary"):
    with st.spinner("Menghitung..."):
        alpha          = cronbach_alpha(df_analysis, items_to_use)
        alpha_del_df   = alpha_if_item_deleted(df_analysis, items_to_use)
        st.session_state["cronbach_alpha"]    = alpha
        st.session_state["alpha_deleted_df"]  = alpha_del_df
        st.session_state["reliability_items"] = items_to_use

if "cronbach_alpha" in st.session_state:
    alpha          = st.session_state["cronbach_alpha"]
    alpha_del_df   = st.session_state["alpha_deleted_df"]

    color_map = {"green":"#27ae60","orange":"#f39c12","orangered":"#e67e22","red":"#e74c3c","gray":"#95a5a6"}
    bg_color  = color_map.get(interpret_alpha_color(alpha), "#3498db")

    # Gauge chart
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=alpha if alpha is not None else 0,
        title={"text": "Cronbach Alpha (α)", "font": {"size": 18}},
        gauge={
            "axis": {"range": [0, 1]},
            "bar":  {"color": bg_color},
            "steps": [
                {"range": [0.00, 0.60], "color": "#fadbd8"},
                {"range": [0.60, 0.70], "color": "#fdebd0"},
                {"range": [0.70, 0.80], "color": "#fef9e7"},
                {"range": [0.80, 0.90], "color": "#eafaf1"},
                {"range": [0.90, 1.00], "color": "#d5f5e3"},
            ],
        },
    ))
    fig_gauge.update_layout(height=280, margin=dict(t=30, b=10))
    st.plotly_chart(fig_gauge, use_container_width=True)

    interp = reliability_interpretation(alpha)
    if alpha and alpha >= 0.70:   st.success(interp)
    elif alpha and alpha >= 0.60: st.warning(interp)
    else:                         st.error(interp)

    st.markdown(f"**Cronbach Alpha:** `{alpha}` — {interpret_alpha(alpha)}")

    # Alpha-if-deleted chart
    st.markdown("### 📊 Alpha Jika Item Dihapus")
    st.caption("Jika menghapus suatu item membuat alpha naik signifikan, pertimbangkan untuk menghapusnya.")
    st.plotly_chart(plot_alpha_if_deleted(alpha_del_df, alpha), use_container_width=True)

    # Table
    st.markdown("### 📋 Tabel Alpha Jika Item Dihapus")
    def highlight_increase(row):
        if row["Alpha Jika Dihapus"] is not None and alpha is not None and row["Alpha Jika Dihapus"] > alpha + 0.02:
            return ["background-color: #fff3cd"] * len(row)
        return [""] * len(row)
    st.dataframe(
        alpha_del_df.style.apply(highlight_increase, axis=1,
        hide_index=True,
    ),
        use_container_width=True, hide_index=True
    )

    if alpha is not None:
        improve = alpha_del_df[
            alpha_del_df["Alpha Jika Dihapus"].notna() &
            (alpha_del_df["Alpha Jika Dihapus"] > alpha + 0.02)
        ]["Item"].tolist()
        if improve:
            st.warning(f"⚠️ Menghapus item berikut dapat meningkatkan reliabilitas: **{', '.join(improve)}**")
        else:
            st.success("✅ Tidak ada item yang secara signifikan menurunkan reliabilitas.")

    # Legenda kode pertanyaan
    _, legend_df = __import__('modules.visualizations', fromlist=['make_short_labels']).make_short_labels(items_to_use)
    if any(legend_df["Kode"].values != legend_df["Pertanyaan"].values):
        with st.expander("📖 Keterangan kode pertanyaan di grafik"):
            st.dataframe(legend_df, use_container_width=True, hide_index=True)

    st.download_button(
        "⬇️ Unduh Hasil (CSV)",
        alpha_del_df.to_csv(index=False).encode("utf-8"),
        "hasil_reliabilitas.csv", "text/csv"
    )
