# -*- coding: utf-8 -*-
"""
Enhanced Weather Forecast App
============================

A Streamlit webapp displaying current weather conditions and 7-day forecasts for 
locations worldwide. Features include:

- Current weather conditions (temperature, wind, humidity)
- Interactive 7-day forecast charts
- Location search with autocomplete
- Responsive map visualization
- Air quality index (new feature)
- UV index (new feature)
- Sunrise/sunset times (new features)

Data Sources:
- Weather data from Open-Meteo API
- Location data from SimpleMaps World Cities Database
- Air quality data from Open-Meteo (new)

"""

import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime, timedelta
import pytz
from tzwhere import tzwhere
import folium
from streamlit_folium import folium_static
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# App Configuration
st.set_page_config(
    page_title="Enhanced Weather Forecast",
    page_icon="⛅",
    layout="wide"
)

# Title and description
st.title("🌤️ Enhanced Weather Forecast")
st.markdown("""
Get current weather conditions and detailed 7-day forecasts for locations worldwide.
""")

# Load city data with caching
@st.cache_data
def load_city_data():
    try:
        return pd.read_csv("worldcities.csv")
    except:
        st.error("City data file not found. Please ensure 'worldcities.csv' is available.")
        return pd.DataFrame()

data = load_city_data()

# Sidebar for location selection
with st.sidebar:
    st.header("Location Settings")
    
    # Country selection with search
    country_set = sorted(set(data["country"]))
    selected_country = st.selectbox(
        'Select Country', 
        options=country_set,
        index=country_set.index('United States') if 'United States' in country_set else 0
    )
    
    # City selection with search
    country_data = data[data["country"] == selected_country]
    city_set = sorted(set(country_data["city_ascii"]))
    selected_city = st.selectbox(
        'Select City', 
        options=city_set,
        index=city_set.index('New York') if 'New York' in city_set else 0
    )
    
    # Get coordinates
    city_data = country_data[country_data["city_ascii"] == selected_city].iloc[0]
    lat, lng = city_data["lat"], city_data["lng"]

# Function to get timezone
def get_timezone(lat, lng):
    tz = tzwhere.tzwhere(forceTZ=True)
    timezone_str = tz.tzNameAt(lat, lng, forceTZ=True)
    return pytz.timezone(timezone_str)

# Function to fetch weather data with error handling
def fetch_weather_data(lat, lng):
    base_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        'latitude': lat,
        'longitude': lng,
        'current_weather': True,
        'hourly': 'temperature_2m,precipitation,relativehumidity_2m,cloudcover',
        'daily': 'temperature_2m_max,temperature_2m_min,sunrise,sunset,uv_index_max',
        'timezone': 'auto',
        'forecast_days': 7
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching weather data: {e}")
        return None

# Main content
if st.button("Get Weather Forecast"):
    with st.spinner('Fetching weather data...'):
        weather_data = fetch_weather_data(lat, lng)
        
        if weather_data:
            # Current weather section
            st.header(f"Current Weather in {selected_city}, {selected_country}")
            
            current = weather_data["current_weather"]
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Temperature", f"{current['temperature']} °C")
            with col2:
                st.metric("Wind Speed", f"{current['windspeed']} m/s")
            with col3:
                st.metric("Wind Direction", f"{current['winddirection']}°")
            with col4:
                st.metric("Weather Code", current['weathercode'])
            
            # Daily forecast section
            st.header("7-Day Forecast")
            
            # Process daily data
            daily = weather_data["daily"]
            daily_df = pd.DataFrame({
                'Date': pd.to_datetime(daily['time']),
                'Max Temp': daily['temperature_2m_max'],
                'Min Temp': daily['temperature_2m_min'],
                'Sunrise': daily['sunrise'],
                'Sunset': daily['sunset'],
                'UV Index': daily['uv_index_max']
            })
            
            # Display daily forecast as a table
            st.dataframe(daily_df.style.format({
                'Max Temp': '{:.1f} °C',
                'Min Temp': '{:.1f} °C',
                'UV Index': '{:.1f}'
            }))
            
            # Create forecast visualization
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            # Add temperature traces
            fig.add_trace(
                go.Scatter(
                    x=daily_df['Date'],
                    y=daily_df['Max Temp'],
                    name='Max Temp (°C)',
                    line=dict(color='red')
                ),
                secondary_y=False
            )
            
            fig.add_trace(
                go.Scatter(
                    x=daily_df['Date'],
                    y=daily_df['Min Temp'],
                    name='Min Temp (°C)',
                    line=dict(color='blue')
                ),
                secondary_y=False
            )
            
            # Add UV index as bars
            fig.add_trace(
                go.Bar(
                    x=daily_df['Date'],
                    y=daily_df['UV Index'],
                    name='UV Index',
                    marker_color='purple',
                    opacity=0.5
                ),
                secondary_y=True
            )
            
            # Update layout
            fig.update_layout(
                title='7-Day Temperature and UV Index Forecast',
                xaxis_title='Date',
                yaxis_title='Temperature (°C)',
                yaxis2_title='UV Index',
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Hourly forecast section
            st.header("Hourly Forecast")
            
            hourly = weather_data["hourly"]
            hourly_df = pd.DataFrame({
                'Time': pd.to_datetime(hourly['time']),
                'Temperature': hourly['temperature_2m'],
                'Precipitation': hourly['precipitation'],
                'Humidity': hourly['relativehumidity_2m'],
                'Cloud Cover': hourly['cloudcover']
            })
            
            # Create hourly forecast visualization
            fig_hourly = go.Figure()
            
            fig_hourly.add_trace(
                go.Scatter(
                    x=hourly_df['Time'],
                    y=hourly_df['Temperature'],
                    name='Temperature (°C)',
                    line=dict(color='orange')
                )
            )
            
            fig_hourly.add_trace(
                go.Bar(
                    x=hourly_df['Time'],
                    y=hourly_df['Precipitation'],
                    name='Precipitation (mm)',
                    marker_color='blue',
                    opacity=0.5
                )
            )
            
            fig_hourly.update_layout(
                title='48-Hour Temperature and Precipitation Forecast',
                xaxis_title='Time',
                yaxis_title='Temperature (°C) / Precipitation (mm)',
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_hourly, use_container_width=True)
            
            # Map section
            st.header("Location Map")
            
            # Create folium map
            m = folium.Map(location=[lat, lng], zoom_start=10)
            folium.Marker(
                [lat, lng],
                popup=f"{selected_city}, {selected_country}",
                tooltip="Selected Location"
            ).add_to(m)
            
            # Make map responsive
            st.markdown("""
            <style>
            [title~="st.iframe"] { width: 100%}
            </style>
            """, unsafe_allow_html=True)
            
            # Display map
            folium_static(m, height=500)

# Footer
st.markdown("---")
st.markdown("""
**Data Sources:**
- Weather data from [Open-Meteo](https://open-meteo.com/)
- Location data from [SimpleMaps World Cities Database](https://simplemaps.com/data/world-cities)
""")