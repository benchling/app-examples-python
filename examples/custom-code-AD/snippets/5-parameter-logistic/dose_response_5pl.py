"""
Benchling Custom Code Demo 5: Dose-Response 5PL Curve Fitting
=============================================================
5-Parameter Logistic (5PL) model adds an asymmetry parameter to the
standard 4PL, giving a better fit for asymmetric sigmoidal curves —
common in immunoassays and ELISA-based dose-response experiments.

INPUTS:
    inputs[0]: pd.DataFrame with columns:
        - Concentration_uM      (float)
        - Replicate             (int)
        - Signal_%Inhibition    (float)

OUTPUTS:
    - "5pl_parameters"      pd.DataFrame  — EC50, Hill slope, Asymmetry, R², AIC, ± SE
    - "aggregated_data"     pd.DataFrame  — Mean ± SEM per concentration
    - "dose_response_curve" go.Figure     — Interactive 5PL plot with residuals subplot

Supported packages:
allotropy, biopython, lmfit, numpy, openpyxl, pandas, plotly,
pyarrow, pydantic, scikit-learn, scipy, statsmodels
"""

from io import BytesIO
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import NamedTuple
from lmfit import Model


class IOData(NamedTuple):
    name: str
    data: BytesIO | pd.DataFrame | go.Figure


# ---------------------------------------------------------------------------
# 5PL model
# ---------------------------------------------------------------------------
def five_pl(x, bottom, top, ec50, hill, asym):
    """
    5-Parameter Logistic model.
    Extends 4PL with 'asym' (asymmetry / F parameter) which allows the
    upper and lower plateaus to be approached at different rates.
    asym=1.0 reduces exactly to the standard 4PL model.
    """
    return bottom + (top - bottom) / ((1.0 + (ec50 / np.clip(x, 1e-12, None)) ** hill) ** asym)


def fit_5pl(concentrations: np.ndarray, responses: np.ndarray):
    """
    Fit 5PL using lmfit. Returns (result, r_squared, aic).
    Also fits 4PL (asym fixed=1) so AIC can flag if 5PL is warranted.
    """
    model = Model(five_pl)

    # --- 5PL fit ---
    params_5pl = model.make_params(
        bottom=dict(value=float(responses.min()), min=0,    max=20),
        top=   dict(value=float(responses.max()), min=80,   max=110),
        ec50=  dict(value=float(np.median(concentrations)), min=1e-6, max=1e6),
        hill=  dict(value=1.5,  min=0.1,  max=10),
        asym=  dict(value=1.0,  min=0.05, max=10),
    )
    result_5pl = model.fit(responses, params_5pl, x=concentrations)

    # --- 4PL fit (asym locked to 1) for AIC comparison ---
    params_4pl = model.make_params(
        bottom=dict(value=float(responses.min()), min=0,   max=20),
        top=   dict(value=float(responses.max()), min=80,  max=110),
        ec50=  dict(value=float(np.median(concentrations)), min=1e-6, max=1e6),
        hill=  dict(value=1.5, min=0.1, max=10),
        asym=  dict(value=1.0, vary=False),
    )
    result_4pl = model.fit(responses, params_4pl, x=concentrations)

    # R²
    fitted  = result_5pl.best_fit
    ss_res  = float(np.sum((responses - fitted) ** 2))
    ss_tot  = float(np.sum((responses - responses.mean()) ** 2))
    r2      = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0

    return result_5pl, result_4pl, r2


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

    df["Concentration_uM"]   = df["Concentration_uM"].astype(float)
    df["Signal_%Inhibition"] = df["Signal_%Inhibition"].astype(float)

    # --- Aggregate replicates ---
    agg = (
        df.groupby("Concentration_uM")["Signal_%Inhibition"]
        .agg(Mean="mean", SD="std", N="count")
        .reset_index()
    )
    agg.columns = ["Concentration_uM", "Mean_Inhibition", "SD", "N"]
    agg["SEM"] = agg["SD"] / np.sqrt(agg["N"])

    conc = agg["Concentration_uM"].values
    resp = agg["Mean_Inhibition"].values

    # --- Fit 5PL (and 4PL for comparison) ---
    result_5pl, result_4pl, r2 = fit_5pl(conc, resp)
    p = result_5pl.params

    def _se(param):
        return round(float(param.stderr), 4) if param.stderr else None

    # Delta AIC: positive = 5PL is better fit
    delta_aic = result_4pl.aic - result_5pl.aic

    summary = pd.DataFrame({
        "Parameter": ["Bottom (%)", "Top (%)", "EC50 (µM)", "Hill Slope", "Asymmetry (F)", "R²", "AIC (5PL)", "ΔAIC vs 4PL"],
        "Value": [
            round(float(p["bottom"].value), 3),
            round(float(p["top"].value),    3),
            round(float(p["ec50"].value),   4),
            round(float(p["hill"].value),   3),
            round(float(p["asym"].value),   3),
            round(r2, 4),
            round(float(result_5pl.aic), 2),
            round(float(delta_aic), 2),
        ],
        "Std_Error": [
            _se(p["bottom"]), _se(p["top"]), _se(p["ec50"]),
            _se(p["hill"]),   _se(p["asym"]), None, None, None,
        ],
        "Note": [
            "", "", "",
            "", "asym=1.0 → standard 4PL",
            "", "",
            "Positive = 5PL preferred",
        ],
    })

    # --- Smooth fit lines ---
    x_fit   = np.logspace(np.log10(conc.min()), np.log10(conc.max()), 400)
    y_5pl   = five_pl(x_fit, p["bottom"].value, p["top"].value,
                      p["ec50"].value, p["hill"].value, p["asym"].value)
    p4      = result_4pl.params
    y_4pl   = five_pl(x_fit, p4["bottom"].value, p4["top"].value,
                      p4["ec50"].value, p4["hill"].value, 1.0)

    # Residuals (5PL)
    fitted_at_conc = five_pl(conc, p["bottom"].value, p["top"].value,
                             p["ec50"].value, p["hill"].value, p["asym"].value)
    residuals = resp - fitted_at_conc
    ec50_val  = float(p["ec50"].value)

    # --- Build figure: main curve + residuals subplot ---
    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.72, 0.28],
        shared_xaxes=False,
        vertical_spacing=0.12,
        subplot_titles=("5PL Dose-Response Fit", "Residuals"),
    )

    # Individual replicates
    fig.add_trace(go.Scatter(
        x=df["Concentration_uM"], y=df["Signal_%Inhibition"],
        mode="markers",
        marker=dict(symbol="circle-open", size=6, color="#7FBBDA", opacity=0.7),
        name="Replicates",
        showlegend=True,
    ), row=1, col=1)

    # Mean ± SEM
    fig.add_trace(go.Scatter(
        x=agg["Concentration_uM"], y=agg["Mean_Inhibition"],
        error_y=dict(array=agg["SEM"].tolist(), visible=True, color="#1B6CA8"),
        mode="markers",
        marker=dict(size=10, color="#1B6CA8"),
        name="Mean ± SEM",
    ), row=1, col=1)

    # 4PL fit (reference)
    fig.add_trace(go.Scatter(
        x=x_fit, y=y_4pl,
        mode="lines",
        line=dict(color="#AAAAAA", width=1.8, dash="dash"),
        name=f"4PL fit (ΔAIC={delta_aic:+.1f})",
    ), row=1, col=1)

    # 5PL fit
    fig.add_trace(go.Scatter(
        x=x_fit, y=y_5pl,
        mode="lines",
        line=dict(color="#E84545", width=2.5),
        name=f"5PL fit  R²={r2:.4f}",
    ), row=1, col=1)

    # EC50 dashed vertical line using paper-relative x coords on row 1 axes
    fig.add_shape(
        type="line",
        xref="x", yref="y",
        x0=ec50_val, x1=ec50_val,
        y0=-5, y1=110,
        line=dict(color="#888888", width=1.2, dash="dot"),
        row=1, col=1,
    )
    fig.add_annotation(
        x=np.log10(ec50_val), y=55,
        xref="x", yref="y",
        text=f"EC50={ec50_val:.3f} µM",
        showarrow=False,
        font=dict(size=11, color="#555555"),
        bgcolor="rgba(255,255,255,0.7)",
        xanchor="left",
        row=1, col=1,
    )

    # Residuals
    fig.add_trace(go.Scatter(
        x=conc, y=residuals,
        mode="markers+lines",
        marker=dict(size=8, color="#E84545"),
        line=dict(color="#E84545", width=1, dash="dot"),
        name="Residuals",
        showlegend=False,
    ), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=[conc.min(), conc.max()], y=[0, 0],
        mode="lines", line=dict(color="#AAAAAA", width=1),
        showlegend=False, hoverinfo="skip",
    ), row=2, col=1)

    # Set log scale explicitly on both subplots
    fig.update_xaxes(type="log", row=1, col=1)
    fig.update_xaxes(title_text="Concentration (µM)", type="log", row=2, col=1)
    fig.update_yaxes(title_text="% Inhibition", range=[-5, 110], row=1, col=1)
    fig.update_yaxes(title_text="Residual", zeroline=True, row=2, col=1)

    fig.update_layout(
        template="plotly_white",
        legend=dict(x=1.02, y=0.95, xanchor="left"),
        width=860, height=640,
        margin=dict(t=60, r=160),
    )

    return [
        IOData(name="5pl_parameters",     data=summary),
        IOData(name="aggregated_data",     data=agg.round(4)),
        IOData(name="dose_response_curve", data=fig),
    ]
