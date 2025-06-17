# -*- coding: utf-8 -*-
"""
FAO Crop Production Analysis
============================
Analyzing agricultural production trends using FAO dataset
Dataset Columns:
Domain Code, Domain, Area Code (M49), Area, Element Code, Element, 
Item Code (CPC), Item, Year Code, Year, Unit, Value, Flag, Flag Description, Note
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from ipywidgets import interact, Dropdown, IntSlider
import geopandas as gpd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Load and preprocess data
def load_data(filepath):
    # Read dataset with specific columns
    cols = ['Area', 'Item', 'Element', 'Year', 'Value', 'Unit']
    df = pd.read_csv(filepath, usecols=cols)
    
    # Clean and transform data
    df = df.dropna(subset=['Value'])
    df['Year'] = df['Year'].astype(int)
    
    # Pivot to get elements as columns
    pivot_df = df.pivot_table(
        index=['Area', 'Item', 'Year', 'Unit'],
        columns='Element',
        values='Value',
        aggfunc='first'
    ).reset_index()
    
    # Rename columns
    pivot_df.columns = ['Area', 'Item', 'Year', 'Unit', 'Area_harvested', 'Production', 'Yield']
    
    return pivot_df

# Load your dataset - replace 'fao_data.csv' with your actual file
df = load_data('fao_data.csv')

# Show cleaned data
print("Cleaned Data Preview:")
print(df.head())
print("\nAvailable Crops:", df['Item'].unique()[:10])
print("Available Countries:", df['Area'].unique()[:10])

# 3D Visualization 1: Production Analysis
def production_3d_plot(selected_item="Maize (corn)"):
    item_df = df[df['Item'] == selected_item]
    
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Get top 10 countries by production
    top_countries = item_df.groupby('Area')['Production'].max().nlargest(10).index
    item_df = item_df[item_df['Area'].isin(top_countries)]
    
    # Color mapping for countries
    countries = item_df['Area'].unique()
    colors = plt.cm.tab20(np.linspace(0, 1, len(countries)))
    
    for i, country in enumerate(countries):
        country_df = item_df[item_df['Area'] == country]
        ax.scatter(
            country_df['Year'],
            country_df['Area_harvested'],
            country_df['Production'],
            s=country_df['Yield']/5,  # Size by yield
            c=[colors[i]],
            label=country,
            alpha=0.7,
            depthshade=True
        )
    
    ax.set_xlabel('Year', fontsize=12, labelpad=15)
    ax.set_ylabel('Area Harvested (ha)', fontsize=12, labelpad=15)
    ax.set_zlabel('Production (tonnes)', fontsize=12, labelpad=15)
    ax.set_title(f'3D Production Analysis: {selected_item}\n(Bubble Size = Yield)', fontsize=16, pad=20)
    ax.legend(loc='upper left', bbox_to_anchor=(0.8, 0.9))
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Rotate for better viewing angle
    ax.view_init(elev=25, azim=-45)
    
    plt.tight_layout()
    plt.show()

# 3D Visualization 2: Yield vs Area vs Time
def yield_vs_area_3d(selected_country="Afghanistan"):
    country_df = df[df['Area'] == selected_country]
    
    fig = go.Figure()
    
    # Add traces for each crop
    crops = country_df['Item'].unique()[:10]  # Limit to top 10 crops
    for crop in crops:
        crop_df = country_df[country_df['Item'] == crop]
        fig.add_trace(go.Scatter3d(
            x=crop_df['Year'],
            y=crop_df['Area_harvested'],
            z=crop_df['Yield'],
            name=crop,
            mode='markers+lines',
            marker=dict(
                size=5,
                opacity=0.8
            ),
            line=dict(
                width=4,
                color=px.colors.qualitative.Plotly[crops.tolist().index(crop) % 10]
            )
        ))
    
    fig.update_layout(
        title=f'Crop Yield vs Harvested Area Over Time: {selected_country}',
        scene=dict(
            xaxis_title='Year',
            yaxis_title='Area Harvested (ha)',
            zaxis_title='Yield (hg/ha)',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=0.8)
        ),
        height=800,
        margin=dict(r=20, b=20, l=20, t=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    ))
    
    fig.show()

# Interactive Choropleth Map
def create_choropleth(selected_item="Maize (corn)", selected_year=2010):
    year_df = df[(df['Item'] == selected_item) & (df['Year'] == selected_year)]
    
    # Get world map
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    
    # Merge data with world map
    merged = world.merge(
        year_df, 
        how='left', 
        left_on='name', 
        right_on='Area'
    )
    
    # Create plot
    fig, ax = plt.subplots(figsize=(15, 10))
    merged.plot(
        column='Production',
        ax=ax,
        legend=True,
        legend_kwds={'label': "Production (tonnes)"},
        cmap='viridis',
        missing_kwds={"color": "lightgrey", "label": "Missing data"},
        edgecolor='black',
        linewidth=0.3
    )
    
    plt.title(f'Global {selected_item} Production ({selected_year})', fontsize=16)
    plt.axis('off')
    plt.show()

# Time Series Analysis
def time_series_analysis(selected_area="Afghanistan", selected_item="Maize (corn)"):
    filtered = df[(df['Area'] == selected_area) & (df['Item'] == selected_item)]
    
    if filtered.empty:
        print("No data available for this selection")
        return
    
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    # Production line
    ax1.plot(filtered['Year'], filtered['Production'], 'b-', label='Production')
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Production (tonnes)', color='b')
    ax1.tick_params('y', colors='b')
    
    # Create second y-axis for area harvested
    ax2 = ax1.twinx()
    ax2.plot(filtered['Year'], filtered['Area_harvested'], 'r-', label='Area Harvested')
    ax2.set_ylabel('Area Harvested (ha)', color='r')
    ax2.tick_params('y', colors='r')
    
    # Create third y-axis for yield
    ax3 = ax1.twinx()
    ax3.spines['right'].set_position(('outward', 60))
    ax3.plot(filtered['Year'], filtered['Yield'], 'g-', label='Yield')
    ax3.set_ylabel('Yield (hg/ha)', color='g')
    ax3.tick_params('y', colors='g')
    
    plt.title(f'{selected_item} Production in {selected_area}', fontsize=14)
    fig.tight_layout()
    plt.show()

# Create interactive dashboard
def create_dashboard():
    print("""
    FAO CROP PRODUCTION ANALYSIS
    ----------------------------
    Select from the options below:
    1. Global Production 3D Analysis
    2. Country-Specific Yield vs Area
    3. Worldwide Production Map
    4. Time Series Analysis
    """)
    
    choice = input("Enter visualization number (1-4): ")
    
    if choice == '1':
        crops = df['Item'].unique()
        selected = Dropdown(options=crops, value='Maize (corn)', description='Crop:')
        interact(production_3d_plot, selected_item=selected)
        
    elif choice == '2':
        countries = df['Area'].unique()
        selected = Dropdown(options=countries, value='Afghanistan', description='Country:')
        interact(yield_vs_area_3d, selected_country=selected)
        
    elif choice == '3':
        crops = df['Item'].unique()
        years = IntSlider(min=df['Year'].min(), max=df['Year'].max(), value=2010, description='Year:')
        crop_dropdown = Dropdown(options=crops, value='Maize (corn)', description='Crop:')
        interact(create_choropleth, selected_item=crop_dropdown, selected_year=years)
        
    elif choice == '4':
        countries = df['Area'].unique()
        crops = df['Item'].unique()
        country_dropdown = Dropdown(options=countries, value='Afghanistan', description='Country:')
        crop_dropdown = Dropdown(options=crops, value='Maize (corn)', description='Crop:')
        interact(time_series_analysis, selected_area=country_dropdown, selected_item=crop_dropdown)
        
    else:
        print("Invalid selection")

# Run the dashboard
create_dashboard()