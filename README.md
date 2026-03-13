# 📊 Platform Analisis Survei

Aplikasi web analisis kuesioner survei yang dibangun dengan Streamlit.
Seluruh antarmuka menggunakan **Bahasa Indonesia**.

---

## 🚀 Cara Menjalankan

### 1. Persyaratan Sistem
- Python 3.9 atau lebih baru
- pip (Python package manager)

### 2. Instalasi

```bash
# Clone atau ekstrak project
cd survey-analytics-app

# Install dependensi
pip install -r requirements.txt
```

**Catatan untuk sklearn ≥ 1.8:** Jika menggunakan scikit-learn versi 1.8+,
jalankan perintah berikut untuk memperbaiki kompatibilitas `factor_analyzer`:

```bash
python -c "
import factor_analyzer.factor_analyzer as f
import inspect, re
src = inspect.getfile(f)
txt = open(src).read()
txt = txt.replace('force_all_finite=', 'ensure_all_finite=')
open(src, 'w').write(txt)
print('Patched!')
"
```

### 3. Jalankan Aplikasi

```bash
streamlit run app.py
```

Buka browser dan akses: **http://localhost:8501**

---

## 📁 Struktur Project

```
survey-analytics-app/
│
├── app.py                        # Halaman Beranda
├── requirements.txt
├── README.md
│
├── pages/
│   ├── 1_Upload_Data.py          # Upload & preview data
│   ├── 2_Pemeriksaan_Data.py     # Pemeriksaan kualitas data
│   ├── 3_Uji_Validitas.py        # Corrected Item-Total Correlation
│   ├── 4_Uji_Reliabilitas.py     # Cronbach Alpha
│   ├── 5_Analisis_Faktor.py      # EFA: KMO, Bartlett, Scree, Varimax
│   ├── 6_Insight_Survei.py       # Dashboard visual
│   └── 7_Laporan.py              # Export laporan Excel
│
└── modules/
    ├── data_loader.py             # Load CSV/XLSX
    ├── likert_detection.py        # Deteksi item Likert otomatis
    ├── reverse_items.py           # Reverse scoring
    ├── validity_test.py           # Uji validitas
    ├── reliability_test.py        # Uji reliabilitas
    ├── efa_analysis.py            # Analisis Faktor
    ├── interpretation.py          # Interpretasi bahasa Indonesia
    └── visualizations.py          # Semua chart Plotly
```

---

## ✨ Fitur Lengkap

| Fitur | Deskripsi |
|-------|-----------|
| Upload Data | CSV & XLSX |
| Deteksi Likert | Otomatis mendeteksi skala 1–4, 1–5, 1–7 |
| Reverse Item | Transformasi skor pertanyaan negatif |
| Uji Validitas | Corrected Item-Total Correlation (r > 0.30) |
| Uji Reliabilitas | Cronbach Alpha + Alpha-if-Item-Deleted |
| Analisis Faktor | KMO, Bartlett, Scree Plot, Varimax |
| Dashboard | Radar chart, heatmap, distribusi Likert |
| Interpretasi | Otomatis dalam Bahasa Indonesia |
| Laporan | Export Excel multi-sheet |

---

## 📊 Format Data yang Didukung

File harus berformat tabel dengan:
- **Baris pertama:** nama kolom (nama pertanyaan)
- **Baris selanjutnya:** jawaban per responden (angka)

Contoh (skala 1–4):

| Q1 | Q2 | Q3 | Q4 |
|----|----|----|-----|
| 3  | 4  | 2  | 3  |
| 4  | 3  | 3  | 4  |
| 2  | 2  | 1  | 3  |

---

## 🛠️ Teknologi

- **Streamlit** — Framework web app
- **Pandas / NumPy** — Manipulasi data
- **SciPy** — Uji statistik
- **Plotly** — Visualisasi interaktif
- **Factor Analyzer** — Analisis Faktor Eksploratori
- **XlsxWriter** — Export Excel
