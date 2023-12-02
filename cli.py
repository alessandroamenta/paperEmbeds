import argparse
from fetchers import ArxivFetcher
from scrapers import ICCVScraper
import pandas as pd

def scrape_and_save(url, num_papers, output_format):
    fetcher = ArxivFetcher()
    scraper = ICCVScraper(fetcher, num_papers_to_scrape=num_papers)
    papers = scraper.get_publications(url)

    if output_format.lower() == 'csv':
        pd.DataFrame(papers).to_csv('papers_output.csv', index=False)
    # Add more formats if needed

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CLI for scraping ML conference papers")
    parser.add_argument("--url", type=str, required=True, help="Conference URL to scrape")
    parser.add_argument("--num_papers", type=int, default=5, help="Number of papers to scrape")
    parser.add_argument("--format", type=str, default="csv", help="Output format (csv, json, etc.)")
    
    args = parser.parse_args()
    scrape_and_save(args.url, args.num_papers, args.format)