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

# Load environment variables
load_dotenv()

# Initialize embedding storage with API keys and index name
embedding_storage = EmbeddingStorage(
        pinecone_api_key=os.getenv("PINECONE_API_KEY"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        pinecone_index_name="ml-conferences"
    )

# Configure the page
st.set_page_config(page_title="ML Conference Papers Explorer 🔭", layout="wide")

# Cache and read publications from a JSON file
@st.cache_data
def read_parsed_publications(filepath):
    """Read and parse publication data from a JSON file."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        # Format authors as a comma-separated string
        for item in data:
            if isinstance(item.get('authors'), list):
                item['authors'] = ', '.join(item['authors'])
        return data
    except FileNotFoundError:
        st.error("Publication file not found. Please check the file path.")
        return []

# Filter publications based on user query and selections
def filter_publications(publications, query, year, conference):
    """Filter publications by title, authors, year, and conference."""
    filtered = []
    for pub in publications:
        if query.lower() in pub['title'].lower() or query.lower() in pub['authors'].lower():
            if year == 'All' or pub['conference_year'] == year:
                if conference == 'All' or pub['conference_name'] == conference:
                    filtered.append(pub)
    return filtered

# Perform a unified search combining filters and semantic search
def unified_search(publications, query, year, conference, top_k=5):
    """Combine semantic and filter-based search to find relevant papers."""
    filtered = filter_publications(publications, "", year, conference)
    if query:  # Use semantic search if there's a query
        semantic_results = embedding_storage.semantic_search(query, top_k=top_k)
        semantic_ids = [result['id'] for result in semantic_results['matches']]
        filtered = [pub for pub in filtered if pub['title'] in semantic_ids]
    return filtered

# Define file paths and load publications
PUBLICATIONS_FILE = 'papers_repo.json'
existing_papers = read_parsed_publications(PUBLICATIONS_FILE)

# Setup sidebar filters for user selection
st.sidebar.header('Filters 🔍')
selected_year = st.sidebar.selectbox('Year', ['All'] + sorted({paper['conference_year'] for paper in existing_papers}, reverse=True))
selected_conference = st.sidebar.selectbox('Conference', ['All'] + sorted({paper['conference_name'] for paper in existing_papers}))

# Main search interface
search_query = st.text_input("Enter keywords, topics, or author names to find relevant papers:", "")
filtered_papers = unified_search(existing_papers, search_query, selected_year, selected_conference, top_k=10)

# Display search results
if filtered_papers:
    df = pd.DataFrame(filtered_papers)
    st.write(f"Found {len(filtered_papers)} matching papers 🔎", df[['title', 'authors', 'url', 'conference_name', 'conference_year']])
else:
    st.write("No matching papers found. Try adjusting your search criteria.")

# t-SNE plot visualization
@st.cache_data
def read_tsne_data(filepath):
    """Read t-SNE data from a file."""
    with open(filepath, 'r') as f:
        return json.load(f)

tsne_data = read_tsne_data('tsne_results.json')

# Assign colors to conferences for visualization
conference_colors = {
    'ICLR': 'blue',
    'ICCV': 'green',
    'NeurIPS': 'red',
    'CVPR': 'orange',
    'EMNLP': 'purple',
    'WACV': 'brown'
}

# Prepare data for plotting
source = ColumnDataSource({
    'x': [item['x'] for item in tsne_data],
    'y': [item['y'] for item in tsne_data],
    'title': [item['id'] for item in tsne_data],
    'conference_name': [item['conference_name'] for item in tsne_data],
    'color': [conference_colors.get(item['conference_name'], 'grey') for item in tsne_data], 
})

# Setup the plot
p = figure(title='ML Conference Papers Visualization', x_axis_label='Dimension 1', y_axis_label='Dimension 2', width=800, tools="pan,wheel_zoom,reset,save")
hover = HoverTool(tooltips=[('Title', '@title'), ('Conference', '@conference_name')])
p.add_tools(hover)
p.circle('x', 'y', size=5, source=source, alpha=0.6, color='color')

# Render the t-SNE plot
html = file_html(p, CDN, "t-SNE Plot")
components.html(html, height=800)

# Add a footer
st.markdown("---")
st.markdown("🚀 Made by Alessandro Amenta and Cesar Romero, with Python and lots of ❤️ for the ML community.")
