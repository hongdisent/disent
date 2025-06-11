# 📌 Save this as app.py and run using: streamlit run app.py

import streamlit as st
import numpy as np
import plotly.graph_objs as go

st.set_page_config(layout="wide")
st.title("SSVI Local Variance Surface (3D Plot)")

# --- SSVI functions ---
def phi(theta, params):
    gamma, eta, sigma, rho = params
    return eta / pow(theta, gamma)

def SSVI(x, t, params):
    gamma, eta, sigma, rho = params
    theta = sigma * sigma * t
    p = phi(theta, params)
    return 0.5 * theta * (1. + rho * p * x + np.sqrt((p * x + rho)**2 + 1 - rho**2))

def SSVI1(x, t, params):
    gamma, eta, sigma, rho = params
    theta = sigma * sigma * t
    p = phi(theta, params)
    num = 0.5 * theta * p * (p * x + rho * np.sqrt(p**2 * x**2 + 2 * p * rho * x + 1) + rho)
    den = np.sqrt(p**2 * x**2 + 2 * p * rho * x + 1)
    return num / den

def SSVI2(x, t, params):
    gamma, eta, sigma, rho = params
    theta = sigma * sigma * t
    p = phi(theta, params)
    num = 0.5 * theta * p**2 * (1 - rho**2)
    den = (p**2 * x**2 + 2 * p * rho * x + 1) * np.sqrt(p**2 * x**2 + 2 * p * rho * x + 1)
    return num / den

def SSVIt(x, t, params):
    eps = 0.0001
    return (SSVI(x, t + eps, params) - SSVI(x, t - eps, params)) / (2 * eps)

def g(x, t, params):
    w = SSVI(x, t, params)
    w1 = SSVI1(x, t, params)
    w2 = SSVI2(x, t, params)
    return (1 - 0.5 * x * w1 / w)**2 - 0.25 * w1**2 * (0.25 + 1 / w) + 0.5 * w2

def SSVI_LocalVarg(x, t, params):
    return SSVIt(x, t, params) / g(x, t, params)

# --- Sidebar: User Input ---
sigma = st.sidebar.slider("σ (vol of vol)", 0.01, 1.0, 0.36, 0.01)
gamma = st.sidebar.slider("γ (curvature)", 0.01, 1.0, 0.55, 0.01)
eta   = st.sidebar.slider("η (skew slope)",  0.01, 1.0, 0.57, 0.01)
rho   = st.sidebar.slider("ρ (correlation)", -0.99, 0.99, 0.0, 0.01)

params = (gamma, eta, sigma, rho)

# Check consistency
arbitrage_free = gamma - 0.25 * (1 + abs(rho)) > 0
st.sidebar.markdown(f"✅ Arbitrage-free: `{arbitrage_free}`")

# --- Grid ---
xx = np.linspace(-1., 1., 40)
TT = np.linspace(0.1, 2., 40)
xxx, TTT = np.meshgrid(xx, TT)

local_var = np.array([[SSVI_LocalVarg(x, t, params) for x in xx] for t in TT])

# --- Plot ---
fig = go.Figure(data=[go.Surface(
    z=local_var,
    x=xxx,
    y=TTT,
    colorscale='Jet',
    showscale=False
)])

fig.update_layout(
    title="SSVI Local Variance Surface",
    scene=dict(
        xaxis_title="Log-moneyness",
        yaxis_title="Maturity",
        zaxis_title="Local Variance",
        camera=dict(eye=dict(x=1.3, y=-1.5, z=0.8))
    ),
    margin=dict(l=0, r=0, b=0, t=40),
    height=600,
    width=800,
)


st.plotly_chart(fig, use_container_width=True)
