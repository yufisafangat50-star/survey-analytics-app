"""
efa_analysis.py - EFA dengan kompatibilitas sklearn >= 1.8
"""
import pandas as pd
import numpy as np

FACTOR_ANALYZER_AVAILABLE = False

try:
    from factor_analyzer import FactorAnalyzer
    from factor_analyzer.factor_analyzer import calculate_kmo, calculate_bartlett_sphericity

    # Test apakah berfungsi — jika error, lakukan patch lalu import ulang
    import numpy as _np
    _test_df = pd.DataFrame(_np.random.rand(20, 3))
    _fa_test = FactorAnalyzer(n_factors=1, rotation=None)
    try:
        _fa_test.fit(_test_df)
        FACTOR_ANALYZER_AVAILABLE = True
    except TypeError:
        # Patch: ganti force_all_finite dengan ensure_all_finite
        import inspect as _inspect, importlib as _importlib
        import factor_analyzer.factor_analyzer as _fa_mod
        _src = _inspect.getfile(_fa_mod)
        _txt = open(_src, encoding="utf-8").read()
        _txt = _txt.replace("force_all_finite=", "ensure_all_finite=")
        open(_src, "w", encoding="utf-8").write(_txt)
        # Reload module setelah patch
        _importlib.reload(_fa_mod)
        from factor_analyzer import FactorAnalyzer
        from factor_analyzer.factor_analyzer import calculate_kmo, calculate_bartlett_sphericity
        FACTOR_ANALYZER_AVAILABLE = True
except Exception:
    FACTOR_ANALYZER_AVAILABLE = False


def run_kmo_bartlett(df, columns):
    if not FACTOR_ANALYZER_AVAILABLE:
        return None, None, None, None
    data = df[columns].dropna()
    kmo_all, kmo_model = calculate_kmo(data)
    chi_sq, p_value = calculate_bartlett_sphericity(data)
    return float(kmo_model), float(chi_sq), float(p_value), data


def interpret_kmo(kmo_value):
    if kmo_value >= 0.90: return "Sangat Baik (Marvelous)"
    elif kmo_value >= 0.80: return "Baik (Meritorious)"
    elif kmo_value >= 0.70: return "Cukup (Middling)"
    elif kmo_value >= 0.60: return "Lemah (Mediocre)"
    elif kmo_value >= 0.50: return "Buruk (Miserable)"
    else: return "Tidak Dapat Diterima"


def run_efa(df, columns, n_factors=None, rotation="varimax"):
    if not FACTOR_ANALYZER_AVAILABLE:
        return None, None, None, None

    data = df[columns].dropna()
    max_factors = min(len(columns), len(data) - 1)

    fa_full = FactorAnalyzer(n_factors=max_factors, rotation=None)
    fa_full.fit(data)
    eigenvalues, _ = fa_full.get_eigenvalues()

    if n_factors is None:
        n_factors = max(1, int((eigenvalues > 1).sum()))
    n_factors = max(1, min(n_factors, max_factors - 1))

    fa = FactorAnalyzer(n_factors=n_factors, rotation=rotation)
    fa.fit(data)

    loadings_df = pd.DataFrame(
        fa.loadings_,
        index=columns,
        columns=[f"Faktor {i+1}" for i in range(n_factors)],
    )
    variance = fa.get_factor_variance()
    variance_df = pd.DataFrame(
        variance,
        index=["SS Loadings", "Proporsi Varians", "Kumulatif Varians"],
        columns=[f"Faktor {i+1}" for i in range(n_factors)],
    ).T

    return loadings_df, eigenvalues, variance_df, n_factors


def get_factor_assignments(loadings_df, threshold=0.40):
    assignments = {}
    for item in loadings_df.index:
        row = loadings_df.loc[item]
        max_loading = row.abs().max()
        if max_loading >= threshold:
            factor = row.abs().idxmax()
            assignments[item] = (factor, round(float(row[factor]), 3))
        else:
            assignments[item] = ("Tidak ada", None)
    return assignments
