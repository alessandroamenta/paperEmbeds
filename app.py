import os

import streamlit as st
import pandas as pd

from scrapers import ICCVScraper
from fetchers import ArxivFetcher

PAPER_CSV = 'papers_with_abstracts.csv'

# Set page config
st.set_page_config(page_title="Accepted conference papers", layout="wide")

# Sidebar for user inputs
st.sidebar.title("ML Conference Paper Scraper")
st.sidebar.markdown("### Instructions")
st.sidebar.markdown("* Enter the URL of the conference for scraping.")
conference_url = st.sidebar.text_input("Conference URL")

# Main area
st.markdown("""
## Accepted conference papers
This tool allows you to scrape abstracts from major ML conference websites.
Enter the URL of the conference in the sidebar and click 'Scrape Papers' to begin.
""")

def read_existing_papers(file_path):
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return pd.DataFrame()

def scrape_and_save(url):
    fetcher = ArxivFetcher()
    scraper = ICCVScraper(fetcher, num_papers_to_scrape=5)

    try:
        existing_papers = read_existing_papers(PAPER_CSV)
        new_papers = scraper.get_publications(url, existing_papers)
        if new_papers:
            df = pd.DataFrame(new_papers)
            df.to_csv(PAPER_CSV, mode='a', header=not os.path.exists(PAPER_CSV), index=False)
            return df
        else:
            st.info('No new papers to add.')
            return pd.DataFrame()
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return pd.DataFrame()

if st.sidebar.button("Scrape Papers"):
    if conference_url:
        with st.spinner('Scraping papers...'):
            df = scrape_and_save(conference_url)
            st.success('Scraping complete!')
            if not df.empty:
                st.write(df)

# Load and display existing papers
existing_papers = read_existing_papers(PAPER_CSV)
if not existing_papers.empty:
    st.markdown("### Existing Papers")
    st.write(existing_papers)
else:
    st.markdown("No papers found. Please scrape to populate.")

# Additional notes or footer
st.markdown("---")
st.markdown("Developed by [Your Name or Organization]")
st.markdown("© 2023 All Rights Reserved")