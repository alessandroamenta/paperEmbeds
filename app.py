import streamlit as st
import pandas as pd
import json
from store import EmbeddingStorage

# Set page config
st.set_page_config(page_title="Accepted conference papers", layout="wide")

# Read the JSON file containing the parsed publications
@st.cache_data
def read_parsed_publications(filepath):
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        # Ensure authors are consistently formatted as strings
        for item in data:
            if isinstance(item.get('authors'), list):
                item['authors'] = ', '.join(item['authors'])
        return data
    except FileNotFoundError:
        return []

# Function to filter publications
def filter_publications(publications, query, year, conference):
    filtered = []
    for pub in publications:
        if query.lower() in pub['title'].lower() or query.lower() in pub['authors'].lower():
            if year == 'All' or pub['conference_year'] == year:
                if conference == 'All' or pub['conference_name'] == conference:
                    filtered.append(pub)
    return filtered

# Path to the JSON file
PUBLICATIONS_FILE = 'papers_repo.json'

# Load the papers
existing_papers = read_parsed_publications(PUBLICATIONS_FILE)

# Sidebar for filters
st.sidebar.header('Filters')
selected_year = st.sidebar.selectbox('Year', ['All'] + sorted({paper['conference_year'] for paper in existing_papers}, reverse=True))
selected_conference = st.sidebar.selectbox('Conference', ['All'] + sorted({paper['conference_name'] for paper in existing_papers}))

# Main search box
search_query = st.text_input("Search for papers (by title or author):", "")

# Apply filters
filtered_papers = filter_publications(existing_papers, search_query, selected_year, selected_conference)

# Display filtered results
if filtered_papers:
    df = pd.DataFrame(filtered_papers)
    st.write(f"Displaying {len(filtered_papers)} papers", df[['title', 'authors', 'conference_name', 'conference_year']])
else:
    st.write("No matching papers found.")

# Footer
st.markdown("---")
st.markdown("Developed by Alessandro Amenta and Cesar Romero")
st.markdown("© 2024 All Rights Reserved")