"""
data_loader.py - Handles data upload and preprocessing
"""
import pandas as pd
import numpy as np
import streamlit as st
import io


def _auto_convert_datetime(df):
    """
    Deteksi otomatis kolom bertipe object yang isinya tanggal/waktu,
    lalu konversi ke datetime64. Kolom non-datetime dibiarkan apa adanya.
    """
    # Kata kunci nama kolom yang kemungkinan besar berisi datetime
    datetime_keywords = ["timestamp", "tanggal", "date", "time", "waktu", "jam"]

    for col in df.select_dtypes(include="object").columns:
        col_lower = col.lower()

        # Cek nama kolom dulu (cepat)
        is_likely_datetime = any(kw in col_lower for kw in datetime_keywords)

        # Jika nama kolom tidak mengandung kata kunci,
        # coba deteksi dari sample isi kolomnya
        if not is_likely_datetime:
            sample = df[col].dropna().head(5).astype(str).tolist()
            # Cek apakah sample mengandung pola angka/slash/dash yang umum di tanggal
            import re
            datetime_pattern = re.compile(
                r'\d{1,4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,4}'   # 2025/05/20 atau 20-05-2025
                r'|'
                r'\d{1,2}\/\d{1,2}\/\d{2,4}\s+\d{1,2}:\d{2}'  # 5/20/2025 9:16:51
            )
            is_likely_datetime = any(datetime_pattern.search(s) for s in sample)

        if is_likely_datetime:
            try:
                converted = pd.to_datetime(df[col], errors="coerce")
                # Hanya ganti jika konversi berhasil untuk mayoritas baris (>80%)
                success_rate = converted.notna().mean()
                if success_rate >= 0.80:
                    df[col] = converted
            except Exception:
                pass  # Gagal konversi — biarkan tipe aslinya

    return df


def load_data(uploaded_file):
    """Load CSV atau XLSX, lalu otomatis konversi kolom datetime."""
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        else:
            st.error("Format file tidak didukung. Gunakan CSV atau XLSX.")
            return None

        df = _auto_convert_datetime(df)
        return df

    except Exception as e:
        st.error(f"Gagal membaca file: {e}")
        return None


def get_data_summary(df):
    """Return basic dataset summary."""
    return {
        "jumlah_responden": len(df),
        "jumlah_kolom": len(df.columns),
        "missing_total": df.isnull().sum().sum(),
        "missing_per_kolom": df.isnull().sum(),
        "tipe_data": df.dtypes,
    }


def get_numeric_columns(df):
    """Return list of numeric columns."""
    return df.select_dtypes(include=[np.number]).columns.tolist()


def clean_data(df, columns):
    """Drop rows with any missing values in specified columns."""
    return df[columns].dropna()
