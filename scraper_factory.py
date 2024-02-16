from scrapers import ICCVScraper, ICLRScraper
from fetchers import ArxivFetcher

class ScraperFactory:
    @staticmethod
    def get_scraper(url, num_papers_to_scrape):
        if 'ICLR.cc' in url:
            return ICLRScraper(num_papers_to_scrape=num_papers_to_scrape)
        elif 'iccv' in url.lower():
            fetcher = ArxivFetcher()
            return ICCVScraper(fetcher, num_papers_to_scrape=num_papers_to_scrape)
        # Add more elif blocks for other conferences
        else:
            raise ValueError(f"No scraper found for the provided URL: {url}")
