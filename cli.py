import argparse
import json
import logging
import os

from scraper_factory import ScraperFactory
from store import EmbeddingStorage


logging.basicConfig(level=logging.INFO)
JSON_FILE_NAME = 'papers_repo.json'

def scrape_and_save(num_papers, conference_type, year, venue_id=None, url=None):
    # Get the appropriate scraper from the factory
    scraper = ScraperFactory.get_scraper(conference_type, num_papers, venue_id=venue_id, url=url)
    papers = scraper.get_publications(venue_id if conference_type in ('ICLR', 'NeurIPS', 'EMNLP') else url, num_papers=num_papers)
    print("Papers fetched: ", papers)  # Debug line

    # Append conference name and year to each paper
    for paper in papers:
        paper['conference_name'] = conference_type
        paper['conference_year'] = year

    # Read existing data from the JSON file and append new data
    try:
        with open(JSON_FILE_NAME, 'r') as f:
            existing_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []

    existing_data.extend(papers)

    # Write the updated data back to the JSON file
    with open(JSON_FILE_NAME, 'w') as f:
        json.dump(existing_data, f, indent=4)
    logging.info(f"Saved scraped papers to {JSON_FILE_NAME}")

def generate_and_store_embeddings(start_index=0):
    # Load papers from JSON
    with open(JSON_FILE_NAME, 'r') as file:
        papers = json.load(file)

    # Skip to the starting index
    papers_to_process = papers[start_index:]

    # Initialize EmbeddingStorage
    embedding_storage = EmbeddingStorage(
        pinecone_api_key=os.getenv("PINECONE_API_KEY"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        pinecone_index_name="ml-conferences"
    )
    
    # Directly pass the remaining papers to store_embeddings
    embedding_storage.store_embeddings(papers_to_process)

    logging.info(f"Embeddings generated and stored successfully for {len(papers_to_process)} papers starting from index {start_index}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CLI for managing ML conference papers")
    subparsers = parser.add_subparsers(dest='action', help='Available actions')

    # Subparser for scraping
    parser_scrape = subparsers.add_parser('scrape', help='Scrape papers information')
    parser_scrape.add_argument("--num_papers", type=int, help="Number of papers to scrape. If not specified, all available papers will be scraped.")
    parser_scrape.add_argument("--conference_type", type=str, choices=['ICLR', 'ICCV', 'NeurIPS', 'CVPR', 'EMNLP', 'WACV'], required=True, help="Type of conference to scrape")
    parser_scrape.add_argument("--year", type=str, required=True, help="Year of the conference")
    parser_scrape.add_argument("--venue_id", type=str, help="Venue ID to fetch papers from (required for ICLR, EMNLP or NeurIPS)")
    parser_scrape.add_argument("--url", type=str, help="URL to fetch papers from (required for ICCV or CVPR)")

    # Subparser for embedding
    parser_embed = subparsers.add_parser('embed', help='Generate and store embeddings')
    parser_embed.add_argument("--start_index", type=int, default=0, help="Index of the paper to start generating embeddings from.")

    args = parser.parse_args()

    if args.action == 'scrape':
        scrape_and_save(args.num_papers, args.conference_type, args.year, venue_id=args.venue_id, url=args.url)
    elif args.action == 'embed':
        generate_and_store_embeddings(start_index=args.start_index)
    else:
        parser.print_help()

