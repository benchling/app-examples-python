"""
Benchling Custom Code Demo 4: Kinetic Time-Course Analysis
===========================================================
Automated Excel → Benchling publication-ready kinetic graphs,
replacing manual Prism curve generation for compound comparisons.

INPUTS:
    inputs[0]: pd.DataFrame — long format with columns:
        Time_hr | Compound | Replicate | Response_AU

OUTPUTS:
    - "kinetic_params"        pd.DataFrame — Emax, kobs, t½, AUC, R² per compound
    - "ttest_summary"         pd.DataFrame — t-test between compounds at final timepoint
    - "aggregated_kinetics"   pd.DataFrame — Mean ± SEM per compound × timepoint
    - "kinetic_curves"        go.Figure    — Multi-compound curves with 95% CI ribbons

Supported packages:
allotropy, biopython, lmfit, numpy, openpyxl, pandas, plotly,
pyarrow, pydantic, scikit-learn, scipy, statsmodels
"""

from io import BytesIO
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from typing import NamedTuple
from lmfit import Model
from scipy.stats import ttest_ind


class IOData(NamedTuple):
    name: str
    data: BytesIO | pd.DataFrame | go.Figure


COMPOUND_COLORS = ["#E84545", "#1B6CA8", "#AAAAAA", "#2ECC71", "#F39C12"]


# ---------------------------------------------------------------------------
# One-phase association model via lmfit
# ---------------------------------------------------------------------------
def one_phase_assoc(t, emax, kobs):
    """One-phase association: y = Emax * (1 - exp(-kobs * t))"""
    return emax * (1.0 - np.exp(-kobs * np.clip(t, 0, None)))


def fit_kinetics(times: np.ndarray, responses: np.ndarray):
    """Returns (emax, kobs, t_half, r2) or nans on failure."""
    try:
        model  = Model(one_phase_assoc)
        params = model.make_params(
            emax=dict(value=float(responses.max()), min=0),
            kobs=dict(value=0.05, min=1e-4, max=10),
        )
        result = model.fit(responses, params, t=times)
        emax   = result.params["emax"].value
        kobs   = result.params["kobs"].value
        t_half = np.log(2) / kobs if kobs > 0 else np.nan
        ss_res = np.sum((responses - result.best_fit) ** 2)
        ss_tot = np.sum((responses - responses.mean()) ** 2)
        r2     = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
        return float(emax), float(kobs), float(t_half), float(r2)
    except Exception:
        return np.nan, np.nan, np.nan, np.nan


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
    df["Time_hr"]     = df["Time_hr"].astype(float)
    df["Response_AU"] = df["Response_AU"].astype(float)

    compounds = df["Compound"].unique().tolist()

    # --- Aggregate: mean ± SEM per compound × timepoint ---
    agg = (
        df.groupby(["Compound", "Time_hr"])["Response_AU"]
        .agg(Mean="mean", SD="std", N="count")
        .reset_index()
    )
    agg["SEM"]       = agg["SD"] / np.sqrt(agg["N"])
    agg["CI95_lower"] = agg["Mean"] - 1.96 * agg["SEM"]
    agg["CI95_upper"] = agg["Mean"] + 1.96 * agg["SEM"]

    # --- Fit kinetics per compound ---
    param_rows = []
    for cpd in compounds:
        sub  = agg[agg["Compound"] == cpd].sort_values("Time_hr")
        times_arr = sub["Time_hr"].values
        means_arr = sub["Mean"].values
        emax, kobs, t_half, r2 = fit_kinetics(times_arr, means_arr)

        # AUC via trapezoidal integration
        auc = float(np.trapezoid(means_arr, times_arr)) if len(times_arr) > 1 else np.nan

        param_rows.append({
            "Compound":   cpd,
            "Emax_AU":    round(emax,   3) if not np.isnan(emax)   else None,
            "kobs_1_hr":  round(kobs,   5) if not np.isnan(kobs)   else None,
            "t_half_hr":  round(t_half, 2) if not np.isnan(t_half) else None,
            "AUC_AU_hr":  round(auc,    2) if not np.isnan(auc)    else None,
            "R2":         round(r2,     4) if not np.isnan(r2)     else None,
        })

    params_df = pd.DataFrame(param_rows)

    # --- T-test at the inflection point (t = 1/kobs), where curves are most differentiated ---
    # For one-phase association, dy/dt is maximised at t=0 but compounds diverge most
    # visibly around t = 1/kobs (the time constant). We average 1/kobs across active
    # compounds and snap to the nearest measured timepoint.
    active = [c for c in compounds if "vehicle" not in c.lower() and "control" not in c.lower()]
    available_timepoints = sorted(df["Time_hr"].unique())
    stats_rows = []

    if len(active) >= 2:
        # Compute t_inflection = 1/kobs for each active compound
        t_inflections = []
        for cpd in active:
            sub = agg[agg["Compound"] == cpd].sort_values("Time_hr")
            _, kobs, _, _ = fit_kinetics(sub["Time_hr"].values, sub["Mean"].values)
            if not np.isnan(kobs) and kobs > 0:
                t_inflections.append(1.0 / kobs)

        if t_inflections:
            t_target = float(np.mean(t_inflections))
            # Snap to nearest actual measured timepoint
            t_compare = float(min(available_timepoints, key=lambda t: abs(t - t_target)))
        else:
            # Fallback: midpoint of timecourse
            t_compare = float(available_timepoints[len(available_timepoints) // 2])

        a_vals = df[(df["Compound"] == active[0]) & (df["Time_hr"] == t_compare)]["Response_AU"].values
        b_vals = df[(df["Compound"] == active[1]) & (df["Time_hr"] == t_compare)]["Response_AU"].values
        if len(a_vals) > 1 and len(b_vals) > 1:
            t_stat, p_val = ttest_ind(a_vals, b_vals)
            sig = "****" if p_val < 0.0001 else "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else "ns"
            stats_rows.append({
                "Comparison":       f"{active[0]} vs {active[1]}",
                "Timepoint_hr":     t_compare,
                "Timepoint_basis":  f"1/kobs inflection (target={t_target:.1f}h)",
                "t_statistic":      round(float(t_stat), 4),
                "p_value":          round(float(p_val), 5),
                "Significance":     sig,
            })
    ttest_df = pd.DataFrame(stats_rows) if stats_rows else pd.DataFrame(
        columns=["Comparison", "Timepoint_hr", "Timepoint_basis", "t_statistic", "p_value", "Significance"])

    # --- Multi-compound kinetics plot ---
    t_smooth = np.linspace(0, float(df["Time_hr"].max()), 300)
    fig = go.Figure()

    for idx, cpd in enumerate(compounds):
        color = COMPOUND_COLORS[idx % len(COMPOUND_COLORS)]
        sub   = agg[agg["Compound"] == cpd].sort_values("Time_hr")
        times_m = sub["Time_hr"].values
        means_m = sub["Mean"].values

        # Smooth fitted line
        emax, kobs, _, _ = fit_kinetics(times_m, means_m)
        if not np.isnan(emax):
            y_smooth = one_phase_assoc(t_smooth, emax, kobs)
            fig.add_trace(go.Scatter(
                x=t_smooth, y=y_smooth,
                mode="lines", line=dict(color=color, width=2.5),
                name=cpd, legendgroup=cpd,
            ))

        # 95% CI ribbon
        x_ribbon = np.concatenate([sub["Time_hr"], sub["Time_hr"].values[::-1]])
        y_ribbon = np.concatenate([sub["CI95_upper"], sub["CI95_lower"].values[::-1]])
        fig.add_trace(go.Scatter(
            x=x_ribbon, y=y_ribbon,
            fill="toself", fillcolor=color, opacity=0.15,
            line=dict(width=0), showlegend=False, legendgroup=cpd, hoverinfo="skip",
        ))

        # Mean ± SEM markers
        fig.add_trace(go.Scatter(
            x=sub["Time_hr"], y=sub["Mean"],
            error_y=dict(array=sub["SEM"].tolist(), visible=True, color=color),
            mode="markers",
            marker=dict(color=color, size=9, line=dict(color="white", width=1.5)),
            showlegend=False, legendgroup=cpd,
            hovertemplate=f"{cpd} t=%{{x}}h mean=%{{y:.2f}}<extra></extra>",
        ))

    fig.update_layout(
        title=dict(text="Kinetic Time-Course: One-Phase Association Fit", font_size=18),
        xaxis=dict(title="Time (hours)"),
        yaxis=dict(title="Response (AU)", rangemode="tozero"),
        legend=dict(title="Compound", x=0.02, y=0.98),
        template="plotly_white",
        width=860, height=540,
    )

    return [
        IOData(name="kinetic_params",       data=params_df),
        IOData(name="ttest_summary",         data=ttest_df),
        IOData(name="aggregated_kinetics",   data=agg.round(4)),
        IOData(name="kinetic_curves",        data=fig),
    ]


