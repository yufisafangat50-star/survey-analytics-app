"""
interpretation.py - Provides Indonesian language interpretations for all analyses
"""

def validity_interpretation(valid_count, total_count):
    pct = (valid_count / total_count * 100) if total_count > 0 else 0
    if pct == 100:
        return "✅ Semua pertanyaan valid! Kuesioner Anda sudah siap digunakan."
    elif pct >= 70:
        return f"⚠️ Sebagian besar pertanyaan valid ({valid_count} dari {total_count}). Pertanyaan yang tidak valid sebaiknya diperbaiki atau dihapus."
    else:
        return f"❌ Banyak pertanyaan tidak valid ({total_count - valid_count} dari {total_count}). Pertimbangkan untuk merevisi kuesioner secara menyeluruh."


def reliability_interpretation(alpha):
    if alpha is None:
        return "Tidak dapat dihitung. Pastikan ada minimal 2 item."
    if alpha >= 0.90:
        return "🌟 Reliabilitas Sangat Baik! Kuesioner sangat konsisten dalam mengukur konstruk yang dimaksud."
    elif alpha >= 0.80:
        return "✅ Reliabilitas Baik. Kuesioner cukup konsisten dan dapat diandalkan."
    elif alpha >= 0.70:
        return "⚠️ Reliabilitas Cukup. Kuesioner dapat digunakan namun ada ruang untuk perbaikan."
    elif alpha >= 0.60:
        return "⚠️ Reliabilitas Kurang. Pertimbangkan untuk merevisi beberapa pertanyaan."
    else:
        return "❌ Tidak Reliabel. Kuesioner perlu direvisi secara signifikan sebelum digunakan."


def kmo_interpretation(kmo):
    if kmo >= 0.80:
        return "✅ Data sangat sesuai untuk Analisis Faktor."
    elif kmo >= 0.70:
        return "✅ Data cukup sesuai untuk Analisis Faktor."
    elif kmo >= 0.60:
        return "⚠️ Data kurang ideal untuk Analisis Faktor, namun masih dapat digunakan."
    else:
        return "❌ Data tidak sesuai untuk Analisis Faktor. Pertimbangkan untuk meninjau kembali kuesioner."


def bartlett_interpretation(p_value):
    if p_value < 0.05:
        return "✅ Uji Bartlett signifikan (p < 0.05). Data cocok untuk Analisis Faktor."
    else:
        return "❌ Uji Bartlett tidak signifikan. Data mungkin tidak cocok untuk Analisis Faktor."


def efa_factor_interpretation(n_factors):
    return (
        f"Analisis Faktor berhasil mengekstrak **{n_factors} faktor** dari data Anda. "
        "Pertanyaan dengan nilai loading tinggi pada faktor yang sama kemungkinan mengukur konstruk yang sama. "
        "Pertimbangkan untuk memberi nama setiap faktor berdasarkan pertanyaan yang termuat di dalamnya."
    )
