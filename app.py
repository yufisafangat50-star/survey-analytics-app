"""
app.py - Halaman Beranda Platform Analisis Survei
"""
import streamlit as st

st.set_page_config(
    page_title="Platform Analisis Survei",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .hero-card {
        background: linear-gradient(135deg, #1a73e8 0%, #0d47a1 100%);
        padding: 2.5rem 2rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(26,115,232,0.3);
    }
    .hero-card h1 { font-size: 2.2rem; font-weight: 800; margin: 0 0 0.5rem 0; }
    .hero-card p  { font-size: 1rem; opacity: 0.92; max-width: 680px; margin: 0; }

    .feat-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    .feat-card {
        background: white;
        border-radius: 12px;
        padding: 1.2rem 1rem;
        border-top: 4px solid #1a73e8;
        box-shadow: 0 2px 10px rgba(0,0,0,0.07);
    }
    .feat-card h4 { color: #1a73e8; margin: 0 0 0.4rem 0; font-size: 1rem; }
    .feat-card p  { color: #555; font-size: 0.85rem; margin: 0; line-height: 1.4; }

    .step-row { margin-bottom: 0.6rem; font-size: 0.95rem; }
    .step-num {
        display: inline-block;
        background: #1a73e8; color: white;
        border-radius: 50%; width: 26px; height: 26px;
        line-height: 26px; text-align: center;
        font-weight: 700; font-size: 0.85rem;
        margin-right: 8px;
    }
    .info-box {
        background: #e8f0fe;
        border-left: 4px solid #1a73e8;
        padding: 0.9rem 1.1rem;
        border-radius: 0 8px 8px 0;
        font-size: 0.9rem;
        color: #1a3a6e;
        margin-top: 1rem;
    }
    div[data-testid="metric-container"] {
        background: white;
        border-radius: 10px;
        padding: 0.6rem;
        box-shadow: 0 1px 8px rgba(0,0,0,0.08);
    }
</style>
""", unsafe_allow_html=True)

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-card">
    <h1>📊 Platform Analisis Survei</h1>
    <p>Alat profesional untuk menganalisis kuesioner survei Anda — validitas item,
    reliabilitas skala, analisis faktor, hingga dashboard insight.
    Dirancang untuk statistisi maupun pengguna non-statistik.</p>
</div>
""", unsafe_allow_html=True)

# ── Fitur Utama ────────────────────────────────────────────────────────────────
st.subheader("🔍 Fitur Utama Platform")

st.markdown("""
<div class="feat-grid">
    <div class="feat-card">
        <h4>✅ Uji Validitas</h4>
        <p>Korelasi Item-Total Terkoreksi untuk memastikan setiap pertanyaan mengukur hal yang seharusnya.</p>
    </div>
    <div class="feat-card">
        <h4>🔁 Uji Reliabilitas</h4>
        <p>Hitung Cronbach Alpha untuk mengukur konsistensi internal kuesioner Anda.</p>
    </div>
    <div class="feat-card">
        <h4>🧩 Analisis Faktor</h4>
        <p>Temukan struktur tersembunyi dalam data menggunakan Analisis Faktor Eksploratori (EFA).</p>
    </div>
    <div class="feat-card">
        <h4>📈 Dashboard Insight</h4>
        <p>Visualisasi interaktif distribusi jawaban, rata-rata skor, dan perbandingan konstruk.</p>
    </div>
    <div class="feat-card">
        <h4>📝 Interpretasi Otomatis</h4>
        <p>Setiap hasil analisis dilengkapi penjelasan dalam Bahasa Indonesia yang mudah dipahami.</p>
    </div>
    <div class="feat-card">
        <h4>📥 Ekspor Laporan</h4>
        <p>Unduh hasil analisis lengkap dalam format Excel multi-sheet siap pakai.</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Panduan ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("🚀 Cara Menggunakan Platform")

steps = [
    ("Upload Data",        "Unggah file CSV atau XLSX berisi data survei Anda."),
    ("Periksa Data",       "Tinjau kualitas data: missing values, distribusi, dan outlier."),
    ("Pilih Item Likert",  "Konfirmasi pertanyaan berskala Likert dan tandai pertanyaan negatif."),
    ("Jalankan Analisis",  "Lakukan uji validitas, reliabilitas, dan analisis faktor."),
    ("Lihat Insight",      "Eksplorasi dashboard visual untuk memahami pola data survei."),
    ("Unduh Laporan",      "Ekspor seluruh hasil analisis ke dalam file Excel."),
]
for i, (title, desc) in enumerate(steps, 1):
    st.markdown(
        f'<div class="step-row"><span class="step-num">{i}</span>'
        f'<strong>{title}</strong> — {desc}</div>',
        unsafe_allow_html=True
    )

st.markdown("""
<div class="info-box">
    💡 <strong>Untuk Pengguna Non-Statistik:</strong>
    Setiap analisis dilengkapi penjelasan sederhana tanpa memerlukan latar belakang statistik mendalam.
    Cukup unggah data dan ikuti langkah-langkahnya!
</div>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 Platform Analisis Survei")
    st.markdown("---")
    if "df" in st.session_state and st.session_state["df"] is not None:
        df = st.session_state["df"]
        st.success(f"✅ Data dimuat: {len(df)} responden")
        if "likert_cols" in st.session_state:
            st.info(f"📋 Item Likert: {len(st.session_state['likert_cols'])}")
    else:
        st.warning("⚠️ Belum ada data.\nSilakan upload di halaman **Upload Data**.")
    st.markdown("---")
    st.caption("Platform Analisis Survei v1.0")
