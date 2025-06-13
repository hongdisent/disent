import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time

# Streamlit version of Health and Wealth of Nations
st.set_page_config(page_title="Health and Wealth of Nations", layout="wide")

st.title("Health and Wealth of Nations")
st.markdown("*Interactive visualization showing the relationship between income per capita and life expectancy over time*")

# Sample data generation (replace with your actual data loading)
@st.cache_data
def load_data():
    """Load or generate sample data similar to Gapminder dataset"""
    np.random.seed(42)
    
    countries = [
        "United States", "China", "Japan", "Germany", "India", "United Kingdom",
        "France", "Brazil", "Italy", "Canada", "Russia", "South Korea",
        "Australia", "Spain", "Mexico", "Indonesia", "Netherlands", "Turkey",
        "Saudi Arabia", "Switzerland", "Argentina", "Sweden", "Ireland", "Israel",
        "Nigeria", "South Africa", "Egypt", "Bangladesh", "Vietnam", "Philippines"
    ]
    
    regions = {
        "United States": "North America", "China": "Asia", "Japan": "Asia", 
        "Germany": "Europe", "India": "Asia", "United Kingdom": "Europe",
        "France": "Europe", "Brazil": "South America", "Italy": "Europe", 
        "Canada": "North America", "Russia": "Europe", "South Korea": "Asia",
        "Australia": "Oceania", "Spain": "Europe", "Mexico": "North America", 
        "Indonesia": "Asia", "Netherlands": "Europe", "Turkey": "Asia",
        "Saudi Arabia": "Asia", "Switzerland": "Europe", "Argentina": "South America", 
        "Sweden": "Europe", "Ireland": "Europe", "Israel": "Asia",
        "Nigeria": "Africa", "South Africa": "Africa", "Egypt": "Africa", 
        "Bangladesh": "Asia", "Vietnam": "Asia", "Philippines": "Asia"
    }
    
    years = list(range(1800, 2009))
    data = []
    
    for country in countries:
        region = regions[country]
        base_income = np.random.uniform(200, 50000)
        base_life_exp = np.random.uniform(25, 80)
        base_pop = np.random.uniform(1e6, 1e9)
        
        for year in years:
            # Simulate growth over time
            year_factor = (year - 1800) / 208
            income = base_income * (1 + year_factor * 2) + np.random.normal(0, base_income * 0.1)
            life_exp = base_life_exp + year_factor * 30 + np.random.normal(0, 2)
            population = base_pop * (1 + year_factor) + np.random.normal(0, base_pop * 0.1)
            
            data.append({
                'name': country,
                'region': region,
                'year': year,
                'income': max(200, income),
                'lifeExpectancy': max(25, min(85, life_exp)),
                'population': max(1e6, population)
            })
    
    return pd.DataFrame(data)

# Load data
data = load_data()

# Sidebar controls
st.sidebar.header("Controls")

# Year selection
min_year = int(data['year'].min())
max_year = int(data['year'].max())
initial_year = st.sidebar.selectbox("Initial Year", range(min_year, max_year + 1), index=100)

# Animation controls
st.sidebar.subheader("Animation")
play_animation = st.sidebar.button("▶️ Play Animation")
animation_speed = st.sidebar.slider("Animation Speed (seconds)", 0.1, 2.0, 0.5)

# Filter controls
st.sidebar.subheader("Filters")
selected_regions = st.sidebar.multiselect(
    "Select Regions",
    options=data['region'].unique(),
    default=data['region'].unique()
)

# Main content area
col1, col2 = st.columns([3, 1])

with col1:
    # Year slider (main control)
    current_year = st.slider(
        "Year", 
        min_value=min_year, 
        max_value=max_year, 
        value=initial_year,
        key="year_slider"
    )
    
    # Filter data for current year and selected regions
    current_data = data[
        (data['year'] == current_year) & 
        (data['region'].isin(selected_regions))
    ]
    
    # Create Plotly scatter plot
    fig = px.scatter(
        current_data,
        x='income',
        y='lifeExpectancy',
        size='population',
        color='region',
        hover_name='name',
        hover_data={
            'income': ':,.0f',
            'lifeExpectancy': ':.1f',
            'population': ':,.0f'
        },
        title=f"Health and Wealth of Nations - {current_year}",
        labels={
            'income': 'Income per Capita (USD)',
            'lifeExpectancy': 'Life Expectancy (years)',
            'population': 'Population'
        },
        size_max=60,
        width=900,
        height=600
    )
    
    # Update layout for better appearance
    fig.update_layout(
        xaxis_type="log",
        xaxis_title="Income per Capita (USD)",
        yaxis_title="Life Expectancy (years)",
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        font=dict(size=12),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    # Add year annotation
    fig.add_annotation(
        x=0.95,
        y=0.05,
        xref="paper",
        yref="paper",
        text=str(current_year),
        showarrow=False,
        font=dict(size=40, color="orange"),
        opacity=0.7
    )
    
    # Display the plot
    chart_placeholder = st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Statistics")
    
    # Show current year stats
    st.metric("Current Year", current_year)
    st.metric("Countries Shown", len(current_data))
    
    if not current_data.empty:
        st.metric(
            "Avg Life Expectancy", 
            f"{current_data['lifeExpectancy'].mean():.1f} years"
        )
        st.metric(
            "Avg Income", 
            f"${current_data['income'].mean():,.0f}"
        )
    
    # Region breakdown
    st.subheader("Regions")
    region_counts = current_data['region'].value_counts()
    for region, count in region_counts.items():
        st.write(f"**{region}**: {count} countries")

# Animation functionality
if play_animation:
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, year in enumerate(range(min_year, max_year + 1, 5)):  # Step by 5 years
        # Update data
        animation_data = data[
            (data['year'] == year) & 
            (data['region'].isin(selected_regions))
        ]
        
        # Create new plot
        fig_anim = px.scatter(
            animation_data,
            x='income',
            y='lifeExpectancy',
            size='population',
            color='region',
            hover_name='name',
            hover_data={
                'income': ':,.0f',
                'lifeExpectancy': ':.1f',
                'population': ':,.0f'
            },
            title=f"Health and Wealth of Nations - {year}",
            labels={
                'income': 'Income per Capita (USD)',
                'lifeExpectancy': 'Life Expectancy (years)',
                'population': 'Population'
            },
            size_max=60,
            width=900,
            height=600
        )
        
        fig_anim.update_layout(
            xaxis_type="log",
            xaxis_title="Income per Capita (USD)",
            yaxis_title="Life Expectancy (years)",
            showlegend=True,
            font=dict(size=12),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        # Add year annotation
        fig_anim.add_annotation(
            x=0.95,
            y=0.05,
            xref="paper",
            yref="paper",
            text=str(year),
            showarrow=False,
            font=dict(size=40, color="orange"),
            opacity=0.7
        )
        
        # Update chart
        chart_placeholder.plotly_chart(fig_anim, use_container_width=True)
        
        # Update progress
        progress = (i + 1) / len(range(min_year, max_year + 1, 5))
        progress_bar.progress(progress)
        status_text.text(f'Year: {year}')
        
        # Wait for animation speed
        time.sleep(animation_speed)
    
    status_text.text('Animation complete!')

# Additional information
st.markdown("---")
st.markdown("""
### About this Visualization

This interactive chart shows the relationship between **income per capita** and **life expectancy** 
across different countries and regions over time. Each bubble represents a country, where:

- **X-axis**: Income per capita (logarithmic scale)
- **Y-axis**: Life expectancy in years
- **Bubble size**: Population size
- **Bubble color**: Geographic region

Use the year slider to explore how countries have evolved over time, or click the play button 
to see an animated progression through the years.

*Inspired by Hans Rosling's famous "Health and Wealth of Nations" visualization.*
""")

# Instructions for embedding
st.markdown("---")
st.markdown("""
### 💡 How to Run This in Streamlit

1. Save this code as `gapminder_app.py`
2. Install required packages:
   ```bash
   pip install streamlit plotly pandas numpy
   ```
3. Run the app:
   ```bash
   streamlit run gapminder_app.py
   ```
4. Open your browser to the provided local URL
""")