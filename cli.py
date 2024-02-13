import os
import argparse
import json

from fetchers import ArxivFetcher
from scrapers import ICCVScraper
from store import EmbeddingStorage

JSON_FILE_NAME = 'papers_repository.json'

def scrape_and_save(url, num_papers, output_format):
    fetcher = ArxivFetcher()
    num_papers_to_scrape = None if num_papers == -1 else num_papers
    scraper = ICCVScraper(fetcher, num_papers_to_scrape=num_papers_to_scrape)
    papers = scraper.get_publications(url)

    if output_format.lower() == 'json':
        with open('papers_repository.json', 'w') as f:
            json.dump(papers, f, indent=4)
    elif output_format.lower() == 'jsonl':
        with open('papers_repository.jsonl', 'w') as f:
            for paper in papers:
                f.write(json.dumps(paper) + '\n')

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
    parser.add_argument("--url", type=str, required=True, help="Conference URL to scrape")
    parser.add_argument("--num_papers", type=int, default=5, help="Number of papers to scrape")
    
    args = parser.parse_args()
    
    # Step 1: Scrape and save papers to the predefined JSON file
    scrape_and_save(args.url, args.num_papers, 'json')
    
    # Step 2: Initialize EmbeddingStorage and generate/store embeddings
    embedding_storage = EmbeddingStorage(
        weaviate_url=os.environ.get("WEAVIATE_CLUSTER_URL"),
        weaviate_api_key=os.environ.get("WEAVIATE_API_KEY"),
        openai_api_key=os.environ.get("OPENAI_API_KEY")
    )
    
    generate_and_store_embeddings(embedding_storage)
