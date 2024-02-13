import argparse
import json
from fetchers import ArxivFetcher
from scrapers import ICCVScraper

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CLI for scraping ML conference papers")
    parser.add_argument("--url", type=str, required=True, help="Conference URL to scrape")
    parser.add_argument("--num_papers", type=int, default=5, help="Number of papers to scrape")
    parser.add_argument("--format", type=str, choices=['json', 'jsonl'], default="json", help="Output format (json or jsonl)")
    
    args = parser.parse_args()
    scrape_and_save(args.url, args.num_papers, args.format)
