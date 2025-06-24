import streamlit as st
import numpy as np
import plotly.graph_objects as go
import yfinance as yf
import datetime
import pandas as pd

import yfinance as yf
import numpy as np
from datetime import datetime

# 你的SVI函数
def svi(k, params):
    a, b, rho, m, sigma = params
    return a + b * (rho * (k - m) + np.sqrt((k - m)**2 + sigma**2))

# 计算年化剩余时间
def time_to_expiry(expiry_date, current_date=datetime.today()):
    delta = expiry_date - current_date
    return max(delta.days / 365.0, 0)

# 计算对数行权价
def log_moneyness(strike, forward_price):
    return np.log(strike / forward_price)

# 获取SPY期权数据的伪代码流程
def fetch_options_data(ticker):
    spy = yf.Ticker(ticker)
    
    # 获取所有可用到期日列表
    expirations = spy.options
    
    all_data = []
    for expiry_str in expirations:
        expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d")
        T = time_to_expiry(expiry_date)
        if T <= 0:
            continue  # 跳过已到期或当天到期的
        
        # 获取该到期日的期权链数据
        opt_chain = spy.option_chain(expiry_str)
        calls = opt_chain.calls
        
        # 计算远期价格（简化估计，实际可用无风险利率和股息调整）
        spot_price = spy.history(period="1d")["Close"].iloc[-1]
        forward_price = spot_price  # 简单近似
        
        # 过滤出OTM看涨期权（strike > spot）
        calls_otm = calls[calls['strike'] > spot_price]
        
        for _, row in calls_otm.iterrows():
            strike = row['strike']
            implied_vol = row['impliedVolatility']  # 市场隐含波动率
            k = log_moneyness(strike, forward_price)
            
            all_data.append({
                'expiry': expiry_date,
                'T': T,
                'strike': strike,
                'log_moneyness': k,
                'market_iv': implied_vol,
            })
    return all_data

# 调用示例
ticker = st.text_input("Enter Ticker", "SPY")
spy_options_data = fetch_options_data(ticker)

df = pd.DataFrame(spy_options_data)
k_values = df['log_moneyness'].values
T_values = df['T'].values
K,T = np.meshgrid(k_values, T_values)


# SVI parameters (can be adjusted)
a = st.sidebar.slider("a (SVI parameter)", 0.01, 0.1, 0.05, 0.01)
b = st.sidebar.slider("b (SVI parameter)", 0.0, 0.5, 0.1, 0.01)
rho = st.sidebar.slider("rho (SVI parameter)", -0.99, 0.99, 0.1, 0.01)
m = st.sidebar.slider("m (SVI parameter)", -0.5, 0.5, 0.01, 0.01)
sigma = st.sidebar.slider("sigma (SVI parameter)", 0.1, 0.5, 0.2, 0.01)
params = (a, b, rho, m, sigma)

impli_vol = np.sqrt(np.array([[svi(k,params)/t for k in k_values] for t in T_values]))
st.write(impli_vol.shape)
# --- Plot ---
fig = go.Figure(
    data=[go.Surface(
        z=impli_vol, 
        x=K, 
        y=T, 
        colorscale='Jet',
        showscale=True 
)])
fig.update_layout(
    # title="3D SVI-like Implied Volatility Surface",
    scene=dict(
        xaxis_title="Log-moneyness (k)",
        yaxis_title="Maturity (T)",
        zaxis_title="Implied Volatility",
        camera=dict(eye=dict(x=1.3, y=-1.5, z=0.8))
    ),
    margin=dict(l=0, r=0, b=0, t=40),
    height=600,
    width=800,
)

st.plotly_chart(fig, use_container_width=True)