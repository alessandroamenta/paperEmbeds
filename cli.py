import argparse
import json
import logging

from scraper_factory import ScraperFactory

logging.basicConfig(level=logging.INFO)
JSON_FILE_NAME = 'papers_repo.json'

def scrape_and_save(num_papers, conference_type, year, venue_id=None, url=None):
    # Get the appropriate scraper from the factory
    scraper = ScraperFactory.get_scraper(conference_type, num_papers, venue_id=venue_id, url=url)
    papers = scraper.get_publications(venue_id if conference_type == 'ICLR' else url, num_papers=num_papers)
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CLI for scraping and embedding ML conference papers")
    parser.add_argument("--num_papers", type=int, help="Number of papers to scrape. If not specified, all available papers will be scraped.")
    parser.add_argument("--conference_type", type=str, choices=['ICLR', 'ICCV'], required=True, help="Type of conference to scrape")
    parser.add_argument("--year", type=str, required=True, help="Year of the conference")
    parser.add_argument("--venue_id", type=str, help="Venue ID to fetch papers from (required for ICLR)")
    parser.add_argument("--url", type=str, help="URL to fetch papers from (required for ICCV)")
    args = parser.parse_args()

    # Validate input based on the type of conference
    if args.conference_type == 'ICLR' and not args.venue_id:
        parser.error("ICLR scraping requires a venue_id.")
    if args.conference_type == 'ICCV' and not args.url:
        parser.error("ICCV scraping requires a url.")
    
    scrape_and_save(args.num_papers, args.conference_type, args.year, venue_id=args.venue_id, url=args.url)

    # Step 2: Initialize EmbeddingStorage and generate/store embeddings
    #embedding_storage = EmbeddingStorage(
    #    pinecone_api_key=os.getenv("PINECONE_API_KEY"),
    #    openai_api_key=os.getenv("OPENAI_API_KEY"),
    #    pinecone_index_name="ml-conferences"
    #)


    #generate_and_store_embeddings(embedding_storage)
