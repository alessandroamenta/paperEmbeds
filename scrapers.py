import logging
from bs4 import BeautifulSoup
import requests

# Configure logging for your module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Scraper:
    def get_publications(self, url):
        raise NotImplementedError("Subclasses must implement this method!")

class ICCVScraper(Scraper):
    def __init__(self, fetcher, num_papers_to_scrape=None):
        self.fetcher = fetcher
        self.num_papers_to_scrape = num_papers_to_scrape
        logger.info("ICCVScraper instance created with fetcher %s and num_papers_to_scrape %s", fetcher, num_papers_to_scrape)

    def get_publications(self, url):
        logger.info("Fetching publications from URL: %s", url)
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error("Request failed for URL %s: %s", url, e)
            return []

        soup = BeautifulSoup(response.content, 'html.parser')
        papers = []

        arxiv_anchors = [anchor for anchor in soup.find_all('a') if 'arXiv' in anchor.text]
        logger.debug("Found %d arXiv anchors", len(arxiv_anchors))

        # If num_papers_to_scrape is defined, limit the number of papers
        if self.num_papers_to_scrape:
            arxiv_anchors = arxiv_anchors[:self.num_papers_to_scrape]
            logger.info("Limiting the number of papers to scrape to %d", self.num_papers_to_scrape)

        for anchor in arxiv_anchors:
            title = anchor.find_previous('dt').text.strip()
            link = anchor['href']
            arxiv_id = link.split('/')[-1]

            abstract, authors = self.fetcher.fetch(arxiv_id)
            papers.append({'title': title, 'url': link, 'abstract': abstract, 'authors': authors})

        logger.info("Successfully fetched %d papers", len(papers))
        return papers
