import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# Load data from SQLite
@st.cache_data
def load_data():
    conn = sqlite3.connect("movies.db")
    query = """
    SELECT 
        omdb.ID,
        omdb.imdbID,
        omdb.Title,
        omdb.Year,
        omdb.Rating AS Rating_m,
        omdb.Runtime,
        omdb.Genre,
        omdb.Released,
        omdb.Director,
        omdb.Writer,
        omdb.imdbRating,
        omdb.imdbVotes,
        omdb.Language,
        omdb.Country,
        omdb.Oscars,
        tomatoes.Rating AS Rating,
        tomatoes.Meter,
        tomatoes.Reviews,
        tomatoes.Fresh,
        tomatoes.Rotten,
        tomatoes.userMeter,
        tomatoes.userRating,
        tomatoes.userReviews,
        tomatoes.BoxOffice,
        tomatoes.Production
    FROM omdb
    JOIN tomatoes ON omdb.ID = tomatoes.ID
    WHERE tomatoes.Reviews >= 10
    """
    df = pd.read_sql_query(query, conn)
    df = df.rename(columns={"Rating_x": "Rating_m", "Rating_y": "Rating"})
    df['has_oscar'] = df['Oscars'].apply(lambda x: "Yes" if x >= 1 else "No")
    conn.close()
    return df

df = load_data()


st.title("🎬 Movie Explorer (Streamlit Edition)")

# Sidebar - Filters
st.sidebar.header("🔍 Filter Movies")
reviews = st.sidebar.slider("Minimum Rotten Tomatoes reviews", 10, 300, 80, step=10)
oscars = st.sidebar.slider("Minimum Oscar wins", 0, 4, 0)
year = st.sidebar.slider("Year released", 1940, 2014, (1970, 2014))
boxoffice = st.sidebar.slider("Box Office (millions)", 0, 800, (0, 800))
raw_genres = df['Genre'].dropna().unique()
all_genres = sorted(set(
    genre.strip()
    for line in raw_genres
    for genre in line.split(",")
))     
genre = st.sidebar.multiselect("🎞️ Select Genres (leave blank for All)",options=all_genres)
genre = ", ".join([g for g in genre])
director = st.sidebar.text_input("Director name contains (e.g. 'Steven')")
cast = st.sidebar.text_input("Cast name contains (e.g. 'Tom Hanks')")
# Axis selectors
axis_vars = {
    "Tomato Meter": "Meter",
    "Tomato Reviews": "Reviews",
    "IMDB Rating": "imdbRating",
    "User Rating": "userRating",
    "Oscar Wins": "Oscars",
    "Box Office": "BoxOffice"
}
xvar = st.sidebar.selectbox("X-axis", list(axis_vars.keys()), index=0)
yvar = st.sidebar.selectbox("Y-axis", list(axis_vars.keys()), index=1)

st.sidebar.info(
    """
    The Tomato meter is a score that represents the percentage of positive reviews a movie or TV show has received from professional critics. 
    A score of 60% or higher is considered "Fresh," while anything below is "Rotten". 
    """
)

st.sidebar.info("""
**ℹ️ About this App**  
Adapted from the original [Movie Explorer Shiny app](https://github.com/rstudio/shiny-examples/tree/main/051-movie-explorer) by [RStudio](https://rstudio.github.io/).  
Data from [OMDb API](http://www.omdbapi.com/), sourced from IMDb and Rotten Tomatoes.  
""")

# Apply filters
filtered = df[
    (df["Reviews"] >= reviews) &
    (df["Oscars"] >= oscars) &
    (df["Year"] >= year[0]) & (df["Year"] <= year[1]) &
    (df["BoxOffice"] >= boxoffice[0] * 1e6) & (df["BoxOffice"] <= boxoffice[1] * 1e6)
]

if genre:
    filtered = filtered[filtered["Genre"].str.contains(genre, na=False, case=False)]
if director:
    filtered = filtered[filtered["Director"].str.contains(director, na=False, case=False)]
if cast:
    filtered = filtered[filtered["Cast"].str.contains(cast, na=False, case=False)]

# Main plot
if not filtered.empty:
    fig = px.scatter(
        filtered,
        x=axis_vars[xvar],
        y=axis_vars[yvar],
        color="has_oscar",
        hover_data=["Title", "Year", "BoxOffice"],
        labels={"has_oscar": "Won Oscar"},
        opacity=0.6,
        color_discrete_map={"Yes": "orange", "No": "gray"}
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No movies match the selected filters.")

# Show number of movies
st.markdown(f"**Number of movies selected:** {filtered.shape[0]}")