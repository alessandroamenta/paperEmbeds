import os
import json
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
import streamlit.components.v1 as components

from bokeh.plotting import figure
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.resources import CDN
from bokeh.embed import file_html

from store import EmbeddingStorage


load_dotenv()

embedding_storage = EmbeddingStorage(
        pinecone_api_key=os.getenv("PINECONE_API_KEY"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        pinecone_index_name="ml-conferences"
    )

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

def unified_search(publications, query, year, conference, top_k=5):
    filtered = filter_publications(publications, "", year, conference)
    if query:  # Perform semantic search only if there's a query
        semantic_results = embedding_storage.semantic_search(query, top_k=top_k)
        semantic_ids = [result['id'] for result in semantic_results['matches']]
        # Filter the publications based on semantic search results and additional filters
        filtered = [pub for pub in filtered if pub['title'] in semantic_ids]
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
# Apply unified search with filters and optional semantic search
filtered_papers = unified_search(existing_papers, search_query, selected_year, selected_conference, top_k=10)

# Display filtered results
if filtered_papers:
    # Display the filtered and/or semantically searched papers
    df = pd.DataFrame(filtered_papers)
    st.write(f"Displaying {len(filtered_papers)} papers", df[['title', 'authors', 'url', 'conference_name', 'conference_year']])
else:
    st.write("No matching papers found.")

# Function to read t-SNE data
@st.cache_data
def read_tsne_data(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

# Read t-SNE data
tsne_data = read_tsne_data('tsne_results.json')

# Create a ColumnDataSource from the t-SNE data
source = ColumnDataSource({
    'x': [item['x'] for item in tsne_data],
    'y': [item['y'] for item in tsne_data],
    'title': [item['id'] for item in tsne_data],
})

# Create a new plot with a title and axis labels
p = figure(title='t-SNE of Papers', x_axis_label='t-SNE 1', y_axis_label='t-SNE 2', width=800, tools="pan,wheel_zoom,reset,save")

# Add a hover tool that will display the ID
hover = HoverTool(tooltips=[('', '@title')])
p.add_tools(hover)

# Add a circle renderer with size, color, and alpha
point_size = 6  # Smaller point size
p.circle('x', 'y', size=point_size, source=source, alpha=0.6, color='seagreen')

# Convert plot to HTML
html = file_html(p, CDN, "t-SNE Plot")

# Streamlit function to display raw HTML
components.html(html, height=800)

# Footer
st.markdown("---")
st.markdown("Developed by Alessandro Amenta and Cesar Romero")