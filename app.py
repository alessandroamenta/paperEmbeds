import streamlit as st
import pandas as pd
import json

# Set page config
st.set_page_config(page_title="Accepted conference papers", layout="wide")

# Read the JSON file containing the parsed publications
@st.cache_data
def read_parsed_publications(filepath):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Function to filter publications by search query
def filter_publications(publications, query):
    query = query.lower()
    return [pub for pub in publications if query in pub['title'].lower() or any(query in author.lower() for author in pub['authors'])]

# Path to the JSON file containing the publications
PUBLICATIONS_FILE = 'papers_repository.json'

# Load existing papers
existing_papers = read_parsed_publications(PUBLICATIONS_FILE)

# Display only the first 10 papers if no search query is made
initial_display_papers = existing_papers[:10]

# User input for search
search_query = st.text_input("Search for papers (by title or author):")

if search_query:
    # Filter publications based on the search query
    filtered_papers = filter_publications(existing_papers, search_query)
    if filtered_papers:
        st.markdown("### Search Results")
        st.write(pd.DataFrame(filtered_papers))
    else:
        st.markdown("No matching papers found.")
else:
    # If no search query, display the first 10 papers
    st.markdown("### Existing Papers (showing first 10)")
    st.write(pd.DataFrame(initial_display_papers))

# Additional notes or footer
st.markdown("---")
st.markdown("Developed by [Your Name or Organization]")
st.markdown("© 2023 All Rights Reserved")
