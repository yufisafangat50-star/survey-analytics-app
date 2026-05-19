"""
visualizations.py - Semua fungsi visualisasi Plotly
Label panjang otomatis dipotong/disingkat untuk keterbacaan chart.
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

COLORS = {
    "valid":   "#2ecc71",
    "invalid": "#e74c3c",
    "primary": "#3498db",
    "secondary": "#9b59b6",
    "warning": "#f39c12",
}

# ── Helper: buat label pendek ──────────────────────────────────────────────────
def make_short_labels(columns, prefix="Q"):
    """
    Jika kolom sudah berbentuk Q1/Q2/... kembalikan apa adanya.
    Jika kolom berupa teks panjang, buat label pendek P1, P2, ...
    Kembalikan (short_labels dict, label_map DataFrame).
    """
    short = {}
    is_already_short = all(
        (str(c).startswith(("Q","q","P","p","Item","item")) and len(str(c)) <= 6)
        for c in columns
    )
    if is_already_short:
        for c in columns:
            short[c] = str(c)
    else:
        for i, c in enumerate(columns, 1):
            short[c] = f"{prefix}{i}"

    label_map = pd.DataFrame({
        "Kode":       [short[c] for c in columns],
        "Pertanyaan": [str(c)   for c in columns],
    })
    return short, label_map


def plot_missing_heatmap(df, columns):
    short, _ = make_short_labels(columns)
    renamed  = df[columns].rename(columns=short)
    fig = px.imshow(
        renamed.isnull().astype(int).T,
        color_continuous_scale=["#eaf6ff", "#e74c3c"],
        title="Peta Nilai Kosong (Missing Value)",
        aspect="auto",
    )
    fig.update_layout(xaxis_title="Responden", yaxis_title="Item", plot_bgcolor="white")
    return fig


def plot_response_distribution(df, columns):
    short, _ = make_short_labels(columns)
    renamed  = df[columns].rename(columns=short)
    melted   = renamed.melt(var_name="Item", value_name="Jawaban").dropna()
    fig = px.histogram(
        melted, x="Jawaban", color="Item", barmode="group",
        title="Distribusi Jawaban Responden",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_layout(xaxis_title="Skor", yaxis_title="Frekuensi",
                      plot_bgcolor="white", legend_title="Item")
    return fig


def plot_boxplot(df, columns):
    short, _ = make_short_labels(columns)
    renamed  = df[columns].rename(columns=short)
    melted   = renamed.melt(var_name="Item", value_name="Skor").dropna()
    fig = px.box(
        melted, x="Item", y="Skor", color="Item",
        title="Distribusi Skor Per Item (Boxplot)",
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    fig.update_layout(
        xaxis_title="Item", yaxis_title="Skor",
        showlegend=False, plot_bgcolor="white",
        height=max(400, 30 * len(columns) + 150),
    )
    return fig


def plot_validity_barchart(validity_df):
    colors = [COLORS["valid"] if "Valid ✅" in str(s) else COLORS["invalid"]
              for s in validity_df["Status"]]
    # Potong label panjang
    labels = [str(x)[:20] + "…" if len(str(x)) > 20 else str(x)
              for x in validity_df["Item"]]
    fig = go.Figure(go.Bar(
        x=labels,
        y=validity_df["Korelasi Item-Total"],
        marker_color=colors,
        text=validity_df["Korelasi Item-Total"].round(3),
        textposition="outside",
        customdata=validity_df["Item"],
        hovertemplate="%{customdata}<br>r = %{y}<extra></extra>",
    ))
    fig.add_hline(y=0.30, line_dash="dash", line_color="gray",
                  annotation_text="Batas Valid (r=0.30)", annotation_position="top right")
    fig.update_layout(
        title="Korelasi Item-Total Terkoreksi",
        xaxis_title="Item", yaxis_title="Korelasi",
        plot_bgcolor="white", xaxis_tickangle=-40,
        height=max(420, 22 * len(validity_df) + 200),
    )
    return fig


def plot_alpha_if_deleted(alpha_df, current_alpha):
    labels = [str(x)[:20] + "…" if len(str(x)) > 20 else str(x)
              for x in alpha_df["Item"]]
    fig = go.Figure(go.Bar(
        x=labels,
        y=alpha_df["Alpha Jika Dihapus"],
        marker_color=COLORS["primary"],
        text=alpha_df["Alpha Jika Dihapus"].round(3),
        textposition="outside",
        customdata=alpha_df["Item"],
        hovertemplate="%{customdata}<br>Alpha = %{y}<extra></extra>",
    ))
    if current_alpha is not None:
        fig.add_hline(y=current_alpha, line_dash="dash", line_color="red",
                      annotation_text=f"Alpha saat ini ({current_alpha})",
                      annotation_position="top right")
    fig.update_layout(
        title="Cronbach Alpha Jika Item Dihapus",
        xaxis_title="Item", yaxis_title="Alpha Jika Dihapus",
        plot_bgcolor="white", xaxis_tickangle=-40,
        height=max(420, 22 * len(alpha_df) + 200),
    )
    return fig


def plot_scree(eigenvalues):
    n = len(eigenvalues)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(1, n+1)), y=eigenvalues,
        mode="lines+markers",
        marker=dict(color=COLORS["primary"], size=8),
        line=dict(width=2), name="Eigenvalue",
    ))
    fig.add_hline(y=1.0, line_dash="dash", line_color="red",
                  annotation_text="Eigenvalue = 1", annotation_position="right")
    fig.update_layout(
        title="Scree Plot", xaxis_title="Nomor Faktor",
        yaxis_title="Eigenvalue", plot_bgcolor="white",
    )
    return fig


def plot_factor_loadings_heatmap(loadings_df):
    """Heatmap dengan label baris dipotong agar tidak overflow."""
    short, _ = make_short_labels(list(loadings_df.index))
    display  = loadings_df.copy()
    display.index = [short[c] for c in loadings_df.index]
    fig = px.imshow(
        display, text_auto=".2f",
        color_continuous_scale="RdBu", zmin=-1, zmax=1,
        title="Heatmap Factor Loading", aspect="auto",
    )
    fig.update_layout(xaxis_title="Faktor", yaxis_title="Item", plot_bgcolor="white")
    return fig


def plot_mean_scores(df, columns, scale_min, scale_max):
    short, _ = make_short_labels(columns)
    means = df[columns].mean().reset_index()
    means.columns = ["Pertanyaan", "Rata-rata"]
    means["Label"] = means["Pertanyaan"].map(short)
    means = means.sort_values("Rata-rata", ascending=True)

    midpoint = (scale_min + scale_max) / 2
    colors   = [COLORS["valid"] if v >= midpoint else COLORS["invalid"]
                for v in means["Rata-rata"]]

    # Tinggi per bar: 45px minimum, lebih besar untuk item banyak
    bar_height = 45
    chart_height = max(400, bar_height * len(columns) + 120)

    fig = go.Figure(go.Bar(
        x=means["Rata-rata"], y=means["Label"],
        orientation="h", marker_color=colors,
        text=means["Rata-rata"].round(2), textposition="outside",
        customdata=means["Pertanyaan"],
        hovertemplate="%{customdata}<br>Rata-rata = %{x}<extra></extra>",
    ))
    fig.add_vline(x=midpoint, line_dash="dash", line_color="gray",
                  annotation_text=f"Tengah Skala ({midpoint})")
    fig.update_layout(
        title="Rata-rata Skor Per Item",
        xaxis_title="Rata-rata Skor", yaxis_title="Item",
        plot_bgcolor="white",
        height=chart_height,
        # Paksa semua item tampil di sumbu Y
        yaxis=dict(
            autorange=True,
            tickmode="array",
            tickvals=means["Label"].tolist(),
            ticktext=means["Label"].tolist(),
        ),
        margin=dict(l=80, r=100, t=60, b=60),
    )
    return fig


def plot_correlation_heatmap(df, columns):
    short, _ = make_short_labels(columns)
    renamed  = df[columns].rename(columns=short)
    corr     = renamed.corr()
    fig = px.imshow(
        corr, text_auto=".2f",
        color_continuous_scale="RdBu", zmin=-1, zmax=1,
        title="Heatmap Korelasi Antar Item", aspect="auto",
    )
    fig.update_layout(plot_bgcolor="white")
    return fig


def plot_likert_stacked(df, columns, scale_min, scale_max):
    short, _    = make_short_labels(columns)
    scale_range = list(range(int(scale_min), int(scale_max)+1))
    color_scale = px.colors.diverging.RdYlGn
    colors      = [color_scale[int(i*(len(color_scale)-1)/(max(len(scale_range)-1,1)))]
                   for i in range(len(scale_range))]
    short_cols  = [short[c] for c in columns]
    pct_data    = {}
    for col in columns:
        counts = df[col].value_counts().reindex(scale_range, fill_value=0)
        pct_data[short[col]] = (counts / counts.sum() * 100).values

    fig = go.Figure()
    for i, val in enumerate(scale_range):
        fig.add_trace(go.Bar(
            name=f"Skor {val}", x=short_cols,
            y=[pct_data[sc][i] for sc in short_cols],
            marker_color=colors[i],
        ))
    fig.update_layout(
        barmode="stack",
        title="Distribusi Persentase Jawaban",
        xaxis_title="Item", yaxis_title="Persentase (%)",
        plot_bgcolor="white", legend_title="Skor",
        height=max(420, 22 * len(columns) + 200),
    )
    return fig


def plot_radar_chart(means_dict):
    labels = list(means_dict.keys())
    values = list(means_dict.values())
    fig = go.Figure(go.Scatterpolar(
        r=values + [values[0]], theta=labels + [labels[0]],
        fill="toself", line_color=COLORS["primary"],
        fillcolor="rgba(52,152,219,0.2)",
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True)),
        title="Radar Chart: Rata-rata Skor per Konstruk",
    )
    return fig


def make_label_legend(columns, prefix="Q"):
    """Buat tabel kode → pertanyaan lengkap untuk ditampilkan di bawah chart."""
    _, label_map = make_short_labels(columns, prefix)
    return label_map
