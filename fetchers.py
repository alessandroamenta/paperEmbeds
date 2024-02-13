'''This module contains classes that fetch publication content from
various sources. Basically strategy pattern.

TODO: Add fetchers for google scholar, dblp, semantic scholar, etc.
TODO: create a publication class that holds the content and metadata.
'''
from abc import ABCMeta, abstractmethod
import logging
import requests
from bs4 import BeautifulSoup
import PyPDF2
import time

# Configure the logger for this module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PublicationFetcher(metaclass=ABCMeta):
    '''Abstract base class for publication fetchers.'''
    @abstractmethod
    def fetch(self, publication_id):
        '''Fetches the publication content from the source and returns it.'''
        raise NotImplementedError("Subclasses must implement this method!")

class ArxivFetcher(PublicationFetcher):
    def fetch(self, arxiv_id):
        logger.debug(f"Attempting to fetch publication {arxiv_id} from arXiv")
        api_url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        
        # Implementing retries with exponential backoff
        max_retries = 5
        retry_delay = 1  # Start with 1 second delay
        for attempt in range(max_retries):
            try:
                response = requests.get(api_url, headers=headers)
                response.raise_for_status()  # Check for HTTP request errors
                logger.debug("Successfully fetched the data on attempt #%d", attempt + 1)
                break  # Success, exit retry loop
            except requests.exceptions.RequestException as e:
                logger.warning("Attempt #%d failed with error: %s. Retrying in %d seconds...", attempt + 1, e, retry_delay)
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
        else:
            # Failed all retries
            logger.error("Failed to fetch publication %s after %d attempts.", arxiv_id, max_retries)
            return None, None

        soup = BeautifulSoup(response.content, 'xml')
        entry = soup.find('entry')
        abstract = entry.find('summary').text.strip()
        authors = [author.find('name').text for author in entry.find_all('author')]

        logger.info("Successfully fetched publication %s from arXiv", arxiv_id)
        return abstract, authors


        # for the full paper content
        #pdf_url = entry.find('link', {'title': 'pdf'})['href']
        #pdf_response = requests.get(pdf_url)
        #pdf_response.raise_for_status()

        #with BytesIO(pdf_response.content) as open_pdf_file:
        #    reader = PyPDF2.PdfReader(open_pdf_file)
        #    content = ""
        #    for page_num in range(len(reader.pages)):
        #        content += reader.pages[page_num].extract_text()