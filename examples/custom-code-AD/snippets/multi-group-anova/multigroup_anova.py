"""
Benchling Custom Code Demo 2: Multi-Group ANOVA + Tukey Post-Hoc
================================================================
Replaces manual copy-paste into Prism for group significance testing.

INPUTS:
    inputs[0]: pd.DataFrame — wide format, one column per group, e.g.:
        Vehicle_Control | Treatment_1mg | Treatment_5mg | Treatment_10mg | Positive_Control

OUTPUTS:
    - "anova_summary"    pd.DataFrame — F-statistic, p-value, result
    - "tukey_pairwise"   pd.DataFrame — All pairwise comparisons + significance stars
    - "descriptive_stats" pd.DataFrame — N, Mean, SD, SEM per group
    - "anova_bar_chart"  go.Figure    — Bar chart with jitter and significance annotations

Supported packages:
allotropy, biopython, lmfit, numpy, openpyxl, pandas, plotly,
pyarrow, pydantic, scikit-learn, scipy, statsmodels
"""

from io import BytesIO
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from typing import NamedTuple
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd


class IOData(NamedTuple):
    name: str
    data: BytesIO | pd.DataFrame | go.Figure


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def custom_code(inputs: list[IOData], **kwargs) -> list[IOData]:
    # --- Load input ---
    df = None
    for i in inputs:
        if isinstance(i.data, pd.DataFrame):
            df = i.data
            break
        elif isinstance(i.data, BytesIO):
            df = pd.read_excel(i.data)
            break
    if df is None:
        raise ValueError("No DataFrame or Excel file found in inputs")

    # Drop any index column that may come from Excel
    if df.columns[0] in ("Sample_ID", "Unnamed: 0"):
        df = df.iloc[:, 1:]

    group_names = list(df.columns)
    groups = {col: df[col].dropna().astype(float).values for col in group_names}

    # --- One-Way ANOVA ---
    f_stat, p_value = stats.f_oneway(*groups.values())
    anova_summary = pd.DataFrame([{
        "Test":        "One-Way ANOVA",
        "F_statistic": round(float(f_stat), 4),
        "p_value":     "<0.0001" if p_value < 0.0001 else (f"{p_value:.2e}" if p_value < 0.001 else round(float(p_value), 4)),
        "Result":      "Significant (p<0.05)" if p_value < 0.05 else "Not Significant",
    }])

    # --- Tukey HSD via statsmodels ---
    all_values = np.concatenate(list(groups.values()))
    all_labels = np.concatenate([[g] * len(v) for g, v in groups.items()])
    tukey = pairwise_tukeyhsd(all_values, all_labels, alpha=0.05)
    tukey_df = pd.DataFrame(data=tukey._results_table.data[1:],
                             columns=tukey._results_table.data[0])
    tukey_df.columns = ["Group1", "Group2", "Mean_Diff", "p_adj", "CI_Lower", "CI_Upper", "Reject_H0"]
    tukey_df["Mean_Diff"] = tukey_df["Mean_Diff"].astype(float).round(4)
    def sig_stars(p):
        if p < 0.0001: return "****"
        if p < 0.001:  return "***"
        if p < 0.01:   return "**"
        if p < 0.05:   return "*"
        return "ns"

    tukey_df["p_adj_float"] = tukey_df["p_adj"].astype(float)
    tukey_df["Significance"] = tukey_df["p_adj_float"].apply(sig_stars)
    tukey_df["p_adj"]        = tukey_df["p_adj_float"].apply(
        lambda p: "<0.0001" if p < 0.0001 else (f"{p:.2e}" if p < 0.001 else round(p, 4))
    )
    tukey_df.drop(columns=["p_adj_float"], inplace=True)

    # --- Descriptive stats ---
    desc = pd.DataFrame({
        "Group": group_names,
        "N":     [len(groups[g])                                    for g in group_names],
        "Mean":  [round(float(groups[g].mean()), 3)                 for g in group_names],
        "SD":    [round(float(groups[g].std(ddof=1)), 3)            for g in group_names],
        "SEM":   [round(float(groups[g].std(ddof=1) /
                  np.sqrt(len(groups[g]))), 3)                      for g in group_names],
    })

    # --- Bar chart ---
    colors = ["#AAAAAA", "#4DAADF", "#1B6CA8", "#0D3F6E", "#E84545"]
    fig = go.Figure()
    np.random.seed(0)

    for i, g in enumerate(group_names):
        sem  = float(groups[g].std(ddof=1) / np.sqrt(len(groups[g])))
        mean = float(groups[g].mean())
        color = colors[i % len(colors)]

        # Jittered individual points
        x_jitter = np.random.uniform(-0.25, 0.25, len(groups[g])) + i
        fig.add_trace(go.Scatter(
            x=x_jitter.tolist(), y=groups[g].tolist(),
            mode="markers", marker=dict(color=color, size=6, opacity=0.55),
            showlegend=False, hovertemplate=f"{g}: %{{y:.2f}}<extra></extra>",
        ))
        # Bar
        fig.add_trace(go.Bar(
            x=[i], y=[mean],
            error_y=dict(type="data", array=[sem], visible=True),
            marker_color=color, marker_line_color="black", marker_line_width=1,
            name=g, width=0.5,
        ))

    # Significance brackets vs Vehicle (group 0)
    # Stack brackets above the tallest bar, spaced by a fixed step
    data_max = max(float(v.mean() + v.std()) for v in groups.values())
    step     = data_max * 0.08
    bracket_level = data_max * 1.12
    annotations = [dict(
        x=0.99, y=0.99, xref="paper", yref="paper",
        text=f"ANOVA: F={f_stat:.2f}, p<0.0001" if p_value < 0.0001 else (f"ANOVA: F={f_stat:.2f}, p={p_value:.2e}" if p_value < 0.001 else f"ANOVA: F={f_stat:.2f}, p={p_value:.4f}"),
        showarrow=False, bgcolor="white", bordercolor="black", borderwidth=1,
    )]

    bracket_idx = 0
    for i, g in enumerate(group_names[1:], 1):
        row = tukey_df[
            ((tukey_df["Group1"] == group_names[0]) & (tukey_df["Group2"] == g)) |
            ((tukey_df["Group1"] == g) & (tukey_df["Group2"] == group_names[0]))
        ]
        if not row.empty and row.iloc[0]["Significance"] != "ns":
            sig  = row.iloc[0]["Significance"]
            y_br = bracket_level + bracket_idx * step
            # Horizontal bar
            fig.add_shape(type="line", x0=0, x1=i, y0=y_br, y1=y_br,
                          line=dict(color="black", width=1.2))
            # Left tick
            fig.add_shape(type="line", x0=0, x1=0, y0=y_br - step * 0.2, y1=y_br,
                          line=dict(color="black", width=1.2))
            # Right tick
            fig.add_shape(type="line", x0=i, x1=i, y0=y_br - step * 0.2, y1=y_br,
                          line=dict(color="black", width=1.2))
            annotations.append(dict(
                x=i / 2, y=y_br + step * 0.15, text=sig,
                showarrow=False, font=dict(size=13),
            ))
            bracket_idx += 1

    y_axis_max = bracket_level + (bracket_idx + 1) * step

    fig.update_layout(
        title=dict(text="Multi-Group Efficacy: One-Way ANOVA + Tukey HSD", font_size=18),
        xaxis=dict(
            tickmode="array",
            tickvals=list(range(len(group_names))),
            ticktext=[g.replace("_", "<br>") for g in group_names],
            title="Treatment Group",
        ),
        yaxis=dict(title="Response (AU)", zeroline=True, range=[0, y_axis_max]),
        template="plotly_white",
        barmode="overlay",
        showlegend=False,
        width=860, height=580,
        annotations=annotations,
    )

    return [
        IOData(name="anova_summary",    data=anova_summary),
        IOData(name="tukey_pairwise",   data=tukey_df),
        IOData(name="descriptive_stats", data=desc),
        IOData(name="anova_bar_chart",  data=fig),
    ]


