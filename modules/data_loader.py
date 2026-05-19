"""
data_loader.py - Handles data upload and preprocessing
"""
import pandas as pd
import numpy as np
import streamlit as st
import io
import csv


def _detect_delimiter(raw_bytes, encoding):
    """Sniff the delimiter from the first few lines of a CSV."""
    try:
        sample = raw_bytes[:4096].decode(encoding, errors='replace')
        dialect = csv.Sniffer().sniff(sample, delimiters=',;\t|')
        return dialect.delimiter
    except Exception:
        # Fallback: hitung kemunculan delimiter umum di baris pertama
        first_line = raw_bytes.split(b'\n')[0].decode(encoding, errors='replace')
        counts = {d: first_line.count(d) for d in [',', ';', '\t', '|']}
        return max(counts, key=counts.get)


def load_data(uploaded_file):
    """Load CSV or XLSX file and return a DataFrame."""
    try:
        if uploaded_file.name.endswith('.csv'):
            # Auto-detect encoding DAN delimiter
            # Menangani CSV dari Excel Indonesia/Eropa (semicolon separator)
            # serta encoding non-UTF-8 (latin-1, cp1252, dll)
            raw_bytes = uploaded_file.read()
            encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
            df = None
            last_error = None
            for enc in encodings_to_try:
                try:
                    delimiter = _detect_delimiter(raw_bytes, enc)
                    df = pd.read_csv(io.BytesIO(raw_bytes), encoding=enc, sep=delimiter)
                    # Sanity check: survei harus punya > 1 kolom
                    if df.shape[1] < 2:
                        for fallback_sep in [';', ',', '\t']:
                            if fallback_sep != delimiter:
                                try:
                                    df_try = pd.read_csv(
                                        io.BytesIO(raw_bytes), encoding=enc, sep=fallback_sep
                                    )
                                    if df_try.shape[1] > df.shape[1]:
                                        df = df_try
                                except Exception:
                                    pass
                    break
                except UnicodeDecodeError as e:
                    last_error = e
                    continue
                except Exception as e:
                    last_error = e
                    continue
            if df is None:
                raise last_error
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        else:
            st.error("Format file tidak didukung. Gunakan CSV atau XLSX.")
            return None
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
