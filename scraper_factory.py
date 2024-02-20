from scrapers import OpenAccessScraper, OpenReviewScraper
from fetchers import ArxivFetcher, OpenReviewFetcher

class ScraperFactory:
    @staticmethod
    def get_scraper(conference_type, num_papers, venue_id=None, url=None):
        if conference_type in ('ICLR', 'NeurIPS', 'EMNLP'):
            if not venue_id:
                raise ValueError("Scraping this conference requires a venue ID.")
            fetcher = OpenReviewFetcher()
            return OpenReviewScraper(fetcher, num_papers)
        elif conference_type in ('ICCV', 'CVPR', 'WACV'):
            if not url:
                raise ValueError("Scraping this conferencerequires a URL.")
            fetcher = ArxivFetcher()
            # Assuming ICCVScraper is defined to handle num_papers in a different way
            return OpenAccessScraper(fetcher, num_papers)
        else:
            raise ValueError(f"No scraper found for the provided conference type: {conference_type}")
