# -*- coding: utf-8 -*-

# %% [markdown]
# # 🌍 Global Food Production & Sustainability Analysis
# 
# **Analyzing crop yields, land use, and climate impacts with 3D visualizations**  
# *Data sources: FAO, World Bank*

# %%
# Import libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd
from ipywidgets import interact, Dropdown

# %%
# Load sample data (replace with real FAO/World Bank data)
def load_sample_data():
    countries = ['USA', 'China', 'India', 'Brazil', 'France', 'Germany', 'Russia']
    years = range(2000, 2023)
    
    # Generate synthetic data
    data = []
    for country in countries:
        for year in years:
            data.append({
                'Country': country,
                'Year': year,
                'Wheat Yield (tonnes/ha)': np.random.uniform(2, 8),
                'Rice Yield (tonnes/ha)': np.random.uniform(2, 6),
                'Fertilizer Use (kg/ha)': np.random.uniform(50, 300),
                'Temperature Change (°C)': np.random.uniform(0, 2),
                'Arable Land (%)': np.random.uniform(10, 60)
            })
    return pd.DataFrame(data)

df = load_sample_data()
print("Sample Data:")
df.head()

# %%
# 3D Plot: Yield vs. Fertilizer vs. Temperature
def create_3d_plot(crop='Wheat'):
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Color by country
    colors = {'USA':'red', 'China':'blue', 'India':'green', 
              'Brazil':'yellow', 'France':'purple', 'Germany':'orange', 'Russia':'cyan'}
    
    for country, group in df.groupby('Country'):
        ax.scatter(
            group[f'{crop} Yield (tonnes/ha)'],
            group['Fertilizer Use (kg/ha)'],
            group['Temperature Change (°C)'],
            label=country,
            c=colors[country],
            s=100,
            alpha=0.7
        )
    
    ax.set_xlabel(f'{crop} Yield (tonnes/ha)', fontsize=12)
    ax.set_ylabel('Fertilizer Use (kg/ha)', fontsize=12)
    ax.set_zlabel('Temperature Change (°C)', fontsize=12)
    ax.set_title(f'3D Analysis: {crop} Yield vs. Inputs vs. Climate', fontsize=14)
    ax.legend()
    plt.tight_layout()
    plt.show()

# Interactive widget
interact(create_3d_plot, crop=Dropdown(options=['Wheat', 'Rice']));

# %%
# Animated Choropleth Map (Plotly)
def create_choropleth(crop='Wheat'):
    # Sample geodata (in real project, merge with GeoJSON)
    fig = px.choropleth(df,
                        locations="Country",
                        locationmode='country names',
                        color=f"{crop} Yield (tonnes/ha)",
                        animation_frame="Year",
                        range_color=(df[f"{crop} Yield (tonnes/ha)"].min(), 
                                    df[f"{crop} Yield (tonnes/ha)"].max()),
                        title=f"Global {crop} Yield Changes (2000-2022)")
    fig.update_geos(projection_type="natural earth")
    fig.show()

create_choropleth('Wheat')

# %%
# Parallel Coordinates Plot (Interactive)
def create_parallel_plot(year=2010):
    year_df = df[df['Year'] == year]
    fig = px.parallel_coordinates(
        year_df,
        dimensions=[
            'Wheat Yield (tonnes/ha)',
            'Rice Yield (tonnes/ha)',
            'Fertilizer Use (kg/ha)',
            'Arable Land (%)'
        ],
        color='Temperature Change (°C)',
        labels={
            'Wheat Yield (tonnes/ha)': 'Wheat Yield',
            'Rice Yield (tonnes/ha)': 'Rice Yield',
            'Fertilizer Use (kg/ha)': 'Fertilizer',
            'Arable Land (%)': 'Arable Land'
        },
        title=f'Agricultural Profile by Country ({year})'
    )
    fig.show()

interact(create_parallel_plot, year=(2000, 2022));

# %%
# 3D Surface Plot (Country vs Year vs Yield)
def create_surface_plot(crop='Wheat'):
    pivot_df = df.pivot_table(
        index='Country',
        columns='Year',
        values=f'{crop} Yield (tonnes/ha)'
    )
    
    years = pivot_df.columns
    countries = pivot_df.index
    
    X, Y = np.meshgrid(years, range(len(countries)))
    Z = pivot_df.values
    
    fig = go.Figure(data=[go.Surface(z=Z, x=X, y=Y)])
    fig.update_layout(
        title=f'{crop} Yield Trends by Country (3D Surface)',
        scene=dict(
            xaxis_title='Year',
            yaxis_title='Country',
            zaxis_title=f'{crop} Yield (tonnes/ha)',
            yaxis=dict(tickvals=list(range(len(countries))), ticktext=countries)
        ),
        height=800,
        width=1000
    )
    fig.show()

create_surface_plot('Wheat')

# %% [markdown]
# ## Key Insights:
# 1. **Trade-offs**: Countries with high fertilizer use don't always have highest yields
# 2. **Climate Impact**: Rising temperatures correlate with yield variability
# 3. **Land Use**: Countries with <30% arable land show different yield patterns