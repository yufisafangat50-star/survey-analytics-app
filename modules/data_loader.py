"""
data_loader.py - Handles data upload and preprocessing
"""
import pandas as pd
import numpy as np
import streamlit as st
import io


def load_data(uploaded_file):
    """Load CSV or XLSX file and return a DataFrame."""
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
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
