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
    def __init__(self, fetcher, num_papers=None):
        self.fetcher = fetcher
        self.num_papers = num_papers
        logger.info("ICCVScraper instance created with fetcher %s and num_papers_to_scrape %s", fetcher, num_papers)

    def get_publications(self, url, num_papers=None):
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
        if self.num_papers:
            arxiv_anchors = arxiv_anchors[:self.num_papers]
            logger.info("Limiting the number of papers to scrape to %d", self.num_papers)

        for anchor in arxiv_anchors:
            title = anchor.find_previous('dt').text.strip()
            link = anchor['href']
            arxiv_id = link.split('/')[-1]

            abstract, authors = self.fetcher.fetch(arxiv_id)
            papers.append({'title': title, 'url': link, 'abstract': abstract, 'authors': authors})

        logger.info("Successfully fetched %d papers", len(papers))
        return papers
    
class ICLRScraper(Scraper):
    def __init__(self, fetcher, num_papers=None):
        self.fetcher = fetcher
        self.num_papers = num_papers
        logger.info("ICLRScraper instance created with fetcher %s and num_papers %s", fetcher, num_papers)

    def get_publications(self, invitation, num_papers=None):
        logger.info("Fetching publications for invitation: %s", invitation)
        papers_data = self.fetcher.fetch_accepted_submissions(invitation, num_papers=num_papers)
        logger.info(f"Fetched data: {papers_data[:5]}")  # Log first 5 for brevity
        papers = []

        for data in papers_data:
            title = data.get('title', 'No title provided')  # Directly access 'title'
            authors = data.get('authors', ['No authors listed'])  # Directly access 'authors', which is already a list
            abstract = data.get('abstract', 'No abstract provided')  # Directly access 'abstract'
            url = data.get('url', 'No URL provided')


            papers.append({
                'title': title,
                'authors': authors,
                'abstract': abstract,
                'url': url
            })
            for paper in papers[:5]:
                logger.debug(f"Processed paper: {paper}")
        

        logger.info("Successfully fetched %d papers", len(papers))
        return papers