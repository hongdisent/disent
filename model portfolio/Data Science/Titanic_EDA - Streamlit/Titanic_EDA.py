import streamlit as st
import seaborn as sns
import plotly.express as px
import pandas as pd
import numpy as np
# Set page config FIRST (non-wide mode)
st.set_page_config(
    page_title="Titanic Explorer",
    page_icon="🚢",
    layout="centered"  # Default centered layout
)
# Load data
@st.cache_data
def load_data():
    df = sns.load_dataset('titanic')
    df['family_size'] = df['sibsp'] + df['parch'] + 1
    df['is_alone'] = df['family_size'] == 1
    return df

df = load_data()

# --- Sidebar Filters (GLOBAL CONTROLS) ---
st.sidebar.header("⚙️ Global Filters")
show_raw = st.sidebar.checkbox("Show raw data", False)
st.sidebar.divider()
st.sidebar.caption("Made with ❤️ by Hong")
selected_classes = st.sidebar.multiselect(
    "Passenger Class",
    options=df['class'].unique(),
    default=df['class'].unique()
)
age_range = st.sidebar.slider(
    "Age Range",
    min_value=0,
    max_value= int(max(df.age)),
    value=(0, 80)
)

selected_sex = st.sidebar.multiselect(
    "Sex",
    options=df['sex'].unique(),
    default=df['sex'].unique()
)

# Apply filters to ALL tabs
filtered_df = df[
    (df['class'].isin(selected_classes)) &
    (df['age'].between(age_range[0], age_range[1])) &
    (df['sex'].isin(selected_sex))
]
# --- Main Content ---
st.title("🚢 Titanic Explorer")
st.caption(f"Showing {len(filtered_df)} of {len(df)} passengers")

st.markdown("""
🌊 Welcome to the Titanic Data Explorer!

Dive into the tragic yet fascinating story of the Titanic through data. This interactive dashboard reveals:

* Who survived? Explore survival rates by class, gender, and age

* Class disparities Compare fares and privileges across passenger tiers

* Passenger profiles Discover age distributions and family patterns


*(Data source: Seaborn's built-in Titanic dataset, containing real passenger records from 1912.)*


""")


tab1, tab2, tab3 = st.tabs(["Survival", "Class Analysis", "Demographics"])

with tab1:
    st.header("💀 Survival Outcomes")
    
    # Interactive sunburst
    fig1 = px.sunburst(
        filtered_df,
        path=['class', 'sex', 'survived'],
        color='survived',
        color_continuous_scale='Bluered'
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    # Survival rate by feature
    st.subheader("📈 Survival Rates")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Overall", f"{filtered_df['survived'].mean()*100:.1f}%")
    with col2:
        by_class = filtered_df.groupby('class')['survived'].mean().reset_index()
        st.dataframe(by_class, hide_index=True)
    with col3:
        by_sex = filtered_df.groupby('sex')['survived'].mean().reset_index()
        st.dataframe(by_sex, hide_index=True)

with tab2:
    st.header("💰 Class Warfare")
    
    # Fare distribution
    fig2 = px.box(
        filtered_df,
        x='class',
        y='fare',
        color='survived',
        points="all",
        hover_data=['age', 'sex']
    )
    st.plotly_chart(fig2, use_container_width=True)
    
    # Interactive histogram
    st.subheader("🎟️ Fare Distribution")
    hist_bins = st.slider("Number of bins", 5, 50, 20, key="fare_bins")
    fig3 = px.histogram(
        filtered_df,
        x='fare',
        nbins=hist_bins,
        color='class',
        barmode='overlay'
    )
    st.plotly_chart(fig3, use_container_width=True)

with tab3:
    st.header("👥 Passenger Demographics")
    
    # Age distribution
    fig4 = px.violin(
        filtered_df,
        y='age',
        x='sex',
        color='survived',
        box=True,
        points="all"
    )
    st.plotly_chart(fig4, use_container_width=True)
    
    # Family size impact
    st.subheader("👨‍👩‍👧‍👦 Family Impact")
    fig5 = px.scatter(
        filtered_df,
        x='age',
        y='family_size',
        color='survived',
        size='fare',
        hover_data=['class', 'sex']
    )
    st.plotly_chart(fig5, use_container_width=True)

    # --- Age Distribution ---
    st.subheader("Age Distribution")
    fig1 = px.histogram(
        filtered_df,  # <-- Filtered!
        x='age',
        color='survived',
        nbins=30
    )
    st.plotly_chart(fig1)

# --- Status Footer ---
st.sidebar.divider()
st.sidebar.caption(f"Filters active: {len(df) - len(filtered_df)} records hidden")
# --- RAW DATA ---
if show_raw:
    st.subheader("📜 Raw Data")
    st.dataframe(df)
# --- FUN FACTS ---
st.divider()
st.subheader("💡 Did You Know?")
fun_fact = np.random.choice([
    "1st class passengers paid up to 512 bucks for a ticket! (≈$15,000 today)",
    "Only 1 in 4 male 3rd class passengers survived",
    "There were 8 couples celebrating their honeymoon on board"
])
st.write(fun_fact)


