from scrapers import ICCVScraper, ICLRScraper
from fetchers import ArxivFetcher, OpenReviewFetcher

class ScraperFactory:
    @staticmethod
    def get_scraper(conference_type, num_papers, venue_id=None, url=None):
        if conference_type == 'ICLR':
            if not venue_id:
                raise ValueError("ICLR scraping requires a venue ID.")
            fetcher = OpenReviewFetcher()
            return ICLRScraper(fetcher, num_papers)
        elif conference_type == 'ICCV':
            if not url:
                raise ValueError("ICCV scraping requires a URL.")
            fetcher = ArxivFetcher()
            # Assuming ICCVScraper is defined to handle num_papers in a different way
            return ICCVScraper(fetcher, num_papers)
        else:
            raise ValueError(f"No scraper found for the provided conference type: {conference_type}")
