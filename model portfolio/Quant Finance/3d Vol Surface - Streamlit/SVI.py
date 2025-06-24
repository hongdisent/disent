import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import plotly.graph_objects as go
import streamlit as st
st.set_page_config(layout="wide")

st.title("3D SVI Implied Volatility Surface")
# --- SVI-like Implied Volatility Surface ---
st.write("""
A 3D SVI Implied Volatility Surface represents the implied volatility of options on a specific underlying asset across different strike prices and maturities, visualized in a three-dimensional plot. 

- X-axis: Time to maturity or days to expiration.
- Y-axis: Strike price or moneyness (strike price relative to the underlying asset price).
- Z-axis: Implied volatility
""")


st.latex(r'''
w(k, \theta) = a + b \left[ \rho (k - m) + \sqrt{(k - m)^2 + \sigma^2} \right]
''')

# Define SVI function for a single maturity
def svi(k, params):
    a, b, rho, m, sigma = params
    return a + b*(rho*(k - m) + np.sqrt((k - m)**2 + sigma**2))

# Generate grid of log-moneyness (k) and maturities (T)
k_min, k_max, k_step = -1.0, 1.0, 0.05
T_min, T_max, T_step = 0.1, 2.0, 0.1

k_values = np.arange(k_min, k_max + k_step, k_step)
T_values = np.arange(T_min, T_max + T_step, T_step)
K, T = np.meshgrid(k_values, T_values)

# SVI parameters (can be adjusted)
a = st.sidebar.slider("a (SVI parameter)", 0.01, 0.1, 0.05, 0.01)
b = st.sidebar.slider("b (SVI parameter)", 0.0, 0.5, 0.1, 0.01)
rho = st.sidebar.slider("rho (SVI parameter)", -0.99, 0.99, 0.1, 0.01)
m = st.sidebar.slider("m (SVI parameter)", -0.5, 0.5, 0.01, 0.01)
sigma = st.sidebar.slider("sigma (SVI parameter)", 0.1, 0.5, 0.2, 0.01)

params = (a, b, rho, m, sigma)

# For each (k, T) pair, calculate implied volatility using SVI-inspired formula
# Example: vary SVI parameters with T
# def implied_vol(k, T, params=None):
#     # a, b, rho, m, sigma = params
#     a = 0.01 + 0.005*T
#     b = 0.1 + 0.02*T
#     rho = -0.3 + 0.1*T
#     m = 0.0
#     sigma = 0.2
#     w = svi(k, a, b, rho, m, sigma)
#     return np.sqrt(w / T) if T > 0 else 0.0

impli_vol = np.sqrt(np.array([[svi(k,params)/t for k in k_values] for t in T_values]))


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




# # reate the figure and 3D axis
# fig = plt.figure(figsize=(10, 7))
# ax = fig.add_subplot(111, projection='3d')

# # Plot the surface
# surf = ax.plot_surface(K, T, Z1, cmap='viridis', linewidth=0, antialiased=True)

# # Customize the plot
# ax.set_xlabel('Log-moneyness (k)')
# ax.set_ylabel('Maturity (T)')
# ax.set_zlabel('Implied Volatility')
# ax.set_title('3D SVI-like Implied Volatility Surface')

# # Add a color bar
# fig.colorbar(surf, shrink=0.5, aspect=10)

# plt.show()
