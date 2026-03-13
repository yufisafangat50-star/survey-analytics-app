# 📋 Platform Analisis Survei Berbasis Web
### *Interactive Survey Analytics Platform built with Python & Streamlit*

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://survey-analytics.streamlit.app/)
![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red?logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-green)

**🔗 Live Demo:** [https://survey-analytics.streamlit.app](https://survey-analytics.streamlit.app/)

---

## 🧩 Tentang Proyek

Platform analisis survei berbasis web yang dirancang untuk membantu peneliti, mahasiswa, dan praktisi dalam menganalisis data kuesioner Likert secara **otomatis, interaktif, dan tanpa perlu coding**.

Dibangun sebagai bagian dari pengembangan kompetensi di bidang **Statistika Terapan** dan **Data Science**, platform ini mengintegrasikan berbagai metode statistik klasik ke dalam antarmuka yang ramah pengguna.

---

## ✨ Fitur Utama

| Fitur | Deskripsi |
|-------|-----------|
| 📂 **Upload Data** | Mendukung CSV & XLSX, auto-deteksi skala Likert (1–4, 1–5, 1–7) |
| 🔍 **Pemeriksaan Data** | Visualisasi missing value, distribusi jawaban, boxplot |
| ✅ **Uji Validitas** | Corrected Item-Total Correlation dengan interpretasi gabungan r & p-value |
| 🔁 **Uji Reliabilitas** | Cronbach Alpha + Alpha-if-Item-Deleted |
| 🧩 **Analisis Faktor** | EFA dengan KMO, Bartlett, Scree Plot, Varimax rotation |
| 📈 **Dashboard Insight** | Rata-rata skor, stacked bar, radar chart, heatmap korelasi |
| 📄 **Laporan Otomatis** | Export hasil ke Excel multi-sheet |

---

## 🛠️ Tech Stack

```
Python 3.10+
├── streamlit        → Web framework & UI
├── pandas / numpy   → Data processing
├── scipy            → Statistical tests (KMO, Bartlett)
├── scikit-learn     → Factor Analysis (EFA)
├── plotly           → Interactive visualizations
└── xlsxwriter       → Excel report generation
```

---

## 🚀 Cara Menjalankan Secara Lokal

```bash
# 1. Clone repository
git clone https://github.com/yufisafangat50-star/survey-analytics-app.git
cd survey-analytics-app

# 2. Install dependencies
pip install -r requirements.txt

# 3. Jalankan aplikasi
streamlit run app.py
```

Aplikasi akan terbuka di `http://localhost:8501`

---

## 📁 Struktur Proyek

```
survey-analytics-app/
├── app.py                    # Halaman beranda
├── requirements.txt
├── pages/
│   ├── 1_Upload_Data.py
│   ├── 2_Pemeriksaan_Data.py
│   ├── 3_Uji_Validitas.py
│   ├── 4_Uji_Reliabilitas.py
│   ├── 5_Analisis_Faktor.py
│   ├── 6_Insight_Survei.py
│   └── 7_Laporan.py
└── modules/
    ├── data_loader.py
    ├── validity_test.py
    ├── reliability_test.py
    ├── efa_analysis.py
    ├── visualizations.py
    └── interpretation.py
```

---

## 📊 Metodologi Statistik

- **Validitas:** Corrected Item-Total Correlation — item valid jika r > 0.30
- **Reliabilitas:** Cronbach's Alpha — reliabel jika α ≥ 0.70
- **EFA:** Kaiser-Meyer-Olkin (KMO), Bartlett's Test of Sphericity, Varimax Rotation
- **Deteksi Likert:** Otomatis mendeteksi skala 1–4, 1–5, dan 1–7

---

## 👤 Author

**Yufi Safangat**
Mahasiswa Statistika | Data Enthusiast

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin)](https://www.linkedin.com/in/yufi-safangat-66b1a9312/)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black?logo=github)](https://github.com/yufisafangat50-star)

---

*Built with ❤️ using Python & Streamlit*
