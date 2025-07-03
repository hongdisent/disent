import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from scipy.optimize import minimize
import seaborn as sns
import streamlit as st
st.set_page_config(layout="wide")

sns.set(style="whitegrid")
np.random.seed(42)

# ---- Setup ----
tickers = st.sidebar.text_area("Enter tickers (separated by commas or newline):", "AAPL, WMT, TSLA, KO, BAC, T, META, NFLX, CRM")
tickers = [ticker.upper() for ticker in tickers.replace('\n', ',').replace(' ',"").split(',') if ticker.strip()]
start_date = st.sidebar.date_input("Start Date", pd.to_datetime('2020-01-01'))
end_date = st.sidebar.date_input("End Date", pd.to_datetime('2022-01-01'))


prices = yf.download(tickers, start=start_date, end=end_date)['Close']
returns = prices.pct_change().dropna()
mean_returns = returns.mean() * 252
cov_matrix = returns.cov() * 252
n = len(tickers)

# ---- Portfolio Optimizers ----

def get_equal_weights():
    return np.repeat(1/n, n)

def get_inv_vol_weights():
    vol = returns.std()
    inv_vol = 1 / vol
    return (inv_vol / inv_vol.sum()).values

def get_gmv_weights():
    def objective(w): return w.T @ cov_matrix @ w
    constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
    bounds = [(0, 1)] * n
    res = minimize(objective, np.repeat(1/n, n), bounds=bounds, constraints=constraints)
    return res.x

def get_markowitz_weights():
    def objective(w): return -((w @ mean_returns) / np.sqrt(w.T @ cov_matrix @ w))
    constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
    bounds = [(0, 1)] * n
    res = minimize(objective, np.repeat(1/n, n), bounds=bounds, constraints=constraints)
    return res.x

def get_risk_parity_weights():
    def risk_contrib(w): return w * (cov_matrix @ w)
    def objective(w):
        rc = risk_contrib(w)
        return np.sum((rc - rc.mean()) ** 2)
    constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
    bounds = [(0, 1)] * n
    res = minimize(objective, np.repeat(1/n, n), bounds=bounds, constraints=constraints)
    return res.x


# ---- Run Evaluations ----

weights = {
    "Markowitz": get_markowitz_weights(),
    "Global Min Var": get_gmv_weights(),
    "Equal Weighted": get_equal_weights(),
    "Inverse Volatility": get_inv_vol_weights(),
    "Vanilla Risk Parity": get_risk_parity_weights()
}

def evaluate_portfolios(weights_dict):
    cr, dd, rc = {}, {}, {}

    for name, w in weights_dict.items():
        port_ret = returns @ w
        cum_ret = (1 + port_ret).cumprod()
        drawdown = (cum_ret.cummax() - cum_ret) / cum_ret.cummax()
        risk_contrib = w * (cov_matrix @ w)
        risk_contrib /= risk_contrib.sum()
        cr[name], dd[name], rc[name] = cum_ret, drawdown, risk_contrib

    return pd.DataFrame(cr), pd.DataFrame(dd), pd.DataFrame(rc)

# Evaluate all
cr, dd, rc = evaluate_portfolios(weights)
df_w = pd.DataFrame(weights, index=tickers).T.reset_index().melt(id_vars='index', var_name='Ticker', value_name='Weight').rename(columns={'index': 'Portfolio'})
df_rc = rc.T.reset_index().melt(id_vars='index', var_name='Ticker', value_name='Risk Contribution').rename(columns={'index': 'Portfolio'})

# ---- Streamlit App ----
st.title("Multi-Strategy Portfolio Construction and Risk Analysis")
st.write("""
This app compares different portfolio construction methods and evaluates allocations, returns, Sharpe ratios, drawdowns, and risk contributions including:
- Markowitz (Mean-Variance Optimization)
- Global Minimum Variance          
- Equal Weighted
- Inverse Volatility
- Vanilla Risk Parity

For stocks: """ + ", ".join(tickers) + f"""
from {start_date} to {end_date}.  
""")

st.sidebar.markdown("""
## Jump to:
- [Asset Weights](#asset-weights-by-portfolio)
- [Cumulative Returns](#cumulative-returns-over-time)
- [Drawdowns](#portfolio-drawdowns)
- [Risk Contributions](#risk-contributions-by-portfolio)
""", unsafe_allow_html=True)


# --- 1. Asset Weights by Portfolio ---
st.markdown("#### Asset Weights by Portfolio", unsafe_allow_html=True)
fig = px.bar(df_w, x="Ticker", y="Weight", color="Portfolio", barmode="group")
fig.update_layout(xaxis_tickangle=45)
st.plotly_chart(fig, use_container_width=True)

# --- 2. Cumulative Returns ---
st.markdown("#### Cumulative Returns Over Time", unsafe_allow_html=True)
fig = px.line(cr,
              labels={"value": "Growth of $1", "index": "Date"})
fig.update_layout(hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

# --- 3. Drawdowns ---
st.markdown("#### Portfolio Drawdowns", unsafe_allow_html=True)
fig = px.line(dd, labels={"value": "Drawdown", "index": "Date"})
fig.update_layout(hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

# --- 4. Risk Contributions ---
st.markdown("#### Risk Contributions by Portfolio", unsafe_allow_html=True)
fig = px.bar(df_rc, x="Ticker", y="Risk Contribution", color="Portfolio", barmode="group")
fig.update_layout(xaxis_tickangle=45)
st.plotly_chart(fig, use_container_width=True)


# col1, col2 = st.columns([1, 1])  # Equal width but stretch to full width

# # --- 3. Drawdowns ---
# with col1:
#     fig_dd = px.line(dd, title="Portfolio Drawdowns",
#                      labels={"value": "Drawdown", "index": "Date"})
#     fig_dd.update_layout(hovermode="x unified")
#     st.plotly_chart(fig_dd, use_container_width=True, key="drawdown_chart")

# # --- 4. Risk Contributions ---
# with col2:
#     fig_rc = px.bar(df_rc, x="Ticker", y="Risk Contribution", color="Portfolio", barmode="group",
#                     title="Risk Contributions by Portfolio")
#     fig_rc.update_layout(xaxis_tickangle=45)
#     st.plotly_chart(fig_rc, use_container_width=False, key="risk_contribution_chart")


