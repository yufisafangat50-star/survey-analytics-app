"""
efa_analysis.py - EFA menggunakan scikit-learn (tanpa factor_analyzer)
Tidak memerlukan patch apapun, kompatibel di semua environment.
"""
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.decomposition import FactorAnalysis
from sklearn.preprocessing import StandardScaler

FACTOR_ANALYZER_AVAILABLE = True  # Selalu True karena pakai sklearn


def run_kmo_bartlett(df, columns):
    """
    Hitung KMO dan Bartlett's test secara manual menggunakan numpy/scipy.
    Tidak bergantung pada factor_analyzer.
    """
    data = df[columns].dropna().values.astype(float)
    n, p = data.shape

    # ── Korelasi matrix ────────────────────────────────────────────────────────
    corr = np.corrcoef(data, rowvar=False)
    corr = np.clip(corr, -0.9999, 0.9999)

    # ── KMO ───────────────────────────────────────────────────────────────────
    try:
        corr_inv  = np.linalg.inv(corr)
        # Partial correlation matrix
        diag_inv  = np.diag(np.sqrt(1 / np.diag(corr_inv)))
        partial   = -diag_inv @ corr_inv @ diag_inv
        np.fill_diagonal(partial, 1.0)

        # MSA per item, lalu KMO global
        r2_sum = np.sum(corr**2) - p          # sum of squared correlations (off-diag)
        p2_sum = np.sum(partial**2) - p       # sum of squared partials (off-diag)
        kmo    = r2_sum / (r2_sum + p2_sum)
    except np.linalg.LinAlgError:
        kmo = 0.0

    # ── Bartlett's Test ───────────────────────────────────────────────────────
    det      = max(np.linalg.det(corr), 1e-300)
    chi_sq   = -(n - 1 - (2*p + 5)/6) * np.log(det)
    df_bar   = p * (p - 1) / 2
    p_value  = 1 - stats.chi2.cdf(chi_sq, df_bar)

    return float(kmo), float(chi_sq), float(p_value), df[columns].dropna()


def interpret_kmo(kmo_value):
    if kmo_value >= 0.90: return "Sangat Baik (Marvelous)"
    elif kmo_value >= 0.80: return "Baik (Meritorious)"
    elif kmo_value >= 0.70: return "Cukup (Middling)"
    elif kmo_value >= 0.60: return "Lemah (Mediocre)"
    elif kmo_value >= 0.50: return "Buruk (Miserable)"
    else: return "Tidak Dapat Diterima"


def run_efa(df, columns, n_factors=None, rotation="varimax"):
    """
    EFA menggunakan sklearn.decomposition.FactorAnalysis.
    rotation: 'varimax' (default) atau None.
    """
    data   = df[columns].dropna().values.astype(float)
    n, p   = data.shape

    # Standarisasi data
    scaler = StandardScaler()
    data_s = scaler.fit_transform(data)

    # ── Estimasi jumlah faktor via eigenvalue PCA ──────────────────────────────
    cov        = np.cov(data_s, rowvar=False)
    eigenvalues, _ = np.linalg.eigh(cov)
    eigenvalues    = eigenvalues[::-1]          # descending

    if n_factors is None:
        n_factors = max(1, int((eigenvalues > 1).sum()))
    n_factors = max(1, min(n_factors, p - 1))

    # ── sklearn FactorAnalysis ─────────────────────────────────────────────────
    fa_rotation = "varimax" if rotation == "varimax" else None
    fa = FactorAnalysis(
        n_components=n_factors,
        rotation=fa_rotation,
        max_iter=1000,
        random_state=42,
    )
    fa.fit(data_s)

    loadings = fa.components_.T          # shape (p, n_factors)

    loadings_df = pd.DataFrame(
        loadings,
        index=columns,
        columns=[f"Faktor {i+1}" for i in range(n_factors)],
    )

    # ── Varians yang dijelaskan ────────────────────────────────────────────────
    ss_loadings = (loadings ** 2).sum(axis=0)
    prop_var    = ss_loadings / p
    cum_var     = np.cumsum(prop_var)

    variance_df = pd.DataFrame({
        "SS Loadings":       ss_loadings,
        "Proporsi Varians":  prop_var,
        "Kumulatif Varians": cum_var,
    }, index=[f"Faktor {i+1}" for i in range(n_factors)])

    return loadings_df, eigenvalues, variance_df, n_factors


def get_factor_assignments(loadings_df, threshold=0.40):
    """Assign setiap item ke faktor dengan loading absolut tertinggi."""
    assignments = {}
    for item in loadings_df.index:
        row      = loadings_df.loc[item]
        max_val  = row.abs().max()
        if max_val >= threshold:
            factor = row.abs().idxmax()
            assignments[item] = (factor, round(float(row[factor]), 3))
        else:
            assignments[item] = ("Tidak ada", None)
    return assignments
