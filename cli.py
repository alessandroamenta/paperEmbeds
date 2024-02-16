import os
import argparse
import json
import logging

from scraper_factory import ScraperFactory
from scrapers import ICLRScraper, ICCVScraper  # Import the necessary scraper classes
from store import EmbeddingStorage
from fetchers import ArxivFetcher, OpenReviewFetcher

logging.basicConfig(level=logging.INFO)


JSON_FILE_NAME = 'papers_repository.json'
ICLR_TEST_FILE_NAME = 'iclr_test.json'


def scrape_and_save(venue_id, num_papers, output_format, conference_type):
    output_file = JSON_FILE_NAME if conference_type == 'ICCV' else ICLR_TEST_FILE_NAME

    if conference_type == 'ICLR':
        fetcher = OpenReviewFetcher()  # Initialize OpenReviewFetcher for ICLR
        papers = fetcher.fetch_accepted_submissions(venue_id)[:num_papers]
    elif conference_type == 'ICCV':
        # Assuming ICCV scraper logic remains unchanged
        fetcher = ArxivFetcher()  # For ICCV, you'd use ArxivFetcher or similar
        scraper = ICCVScraper(fetcher, num_papers_to_scrape=num_papers)
        papers = scraper.get_publications(venue_id)  # Here venue_id is used as URL

    if output_format.lower() == 'json':
        with open(output_file, 'w') as f:
            json.dump(papers, f, indent=4)
        logging.info(f"Saved scraped papers to {output_file}")

def generate_and_store_embeddings(embedding_storage):
    # Read papers from the JSON file
    with open(JSON_FILE_NAME, 'r') as f:
        papers = json.load(f)
    
    # Generate and store embeddings
    abstracts = [paper['abstract'] for paper in papers]
    embeddings = embedding_storage.generate_embeddings(abstracts)
    embedding_storage.store_embeddings(papers, embeddings)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CLI for scraping and embedding ML conference papers")
    parser.add_argument("--venue_id", type=str, required=True, help="Venue ID to fetch papers from")
    parser.add_argument("--num_papers", type=int, default=5, help="Number of papers to scrape")
    parser.add_argument("--conference_type", type=str, choices=['ICLR', 'ICCV'], required=True, help="Type of conference to scrape")
    args = parser.parse_args()
    
    scrape_and_save(args.venue_id, args.num_papers, 'json', args.conference_type)
    
    # Step 2: Initialize EmbeddingStorage and generate/store embeddings
    #embedding_storage = EmbeddingStorage(
    #    pinecone_api_key=os.getenv("PINECONE_API_KEY"),
    #    openai_api_key=os.getenv("OPENAI_API_KEY"),
    #    pinecone_index_name="ml-conferences"
    #)

    # Load papers from the scraped JSON file based on the conference type
    if args.conference_type == 'ICLR':
        with open(ICLR_TEST_FILE_NAME, 'r') as f:
            papers = json.load(f)
    elif args.conference_type == 'ICCV':
        with open(JSON_FILE_NAME, 'r') as f:
            papers = json.load(f)


    #generate_and_store_embeddings(embedding_storage)
