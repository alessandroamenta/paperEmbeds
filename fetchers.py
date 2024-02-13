'''This module contains classes that fetch publication content from
various sources. Basically strategy pattern.

TODO: Add fetchers for google scholar, dblp, semantic scholar, etc.
TODO: create a publication class that holds the content and metadata.
'''
from abc import ABCMeta, abstractmethod
from io import BytesIO
import logging

import requests
from bs4 import BeautifulSoup
import PyPDF2
import time

logger = logging.getLogger('accepted_papers')


class PublicationFetcher(metaclass=ABCMeta):
    '''Abstract base class for publication fetchers.'''
    @abstractmethod
    def fetch(self, publication_id):
        '''Fetches the publication content from the source and returns it.'''
        raise NotImplementedError("Subclasses must implement this method!")


class ArxivFetcher(PublicationFetcher):
    def fetch(self, arxiv_id):
        logger.debug(f"Fetching publication {arxiv_id} from arxiv.org")
        api_url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        
        # Implementing retries with exponential backoff
        max_retries = 5
        retry_delay = 1  # start with 1 second delay
        for attempt in range(max_retries):
            try:
                response = requests.get(api_url, headers=headers)
                response.raise_for_status()  # Check for HTTP request errors
                break  # Success, exit retry loop
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed: {e}, retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
        else:
            # Failed all retries
            logger.error(f"Failed to fetch publication after {max_retries} attempts")
            return None, None

        soup = BeautifulSoup(response.content, 'xml')
        entry = soup.find('entry')
        abstract = entry.find('summary').text.strip()
        authors = [author.find('name').text for author in entry.find_all('author')]

        logger.info(f"Fetched publication {arxiv_id} from arxiv.org")
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