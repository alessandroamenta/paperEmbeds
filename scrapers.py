import logging

from bs4 import BeautifulSoup
import requests


class Scraper:
    def get_publications(self, url):
        raise NotImplementedError("Subclasses must implement this method!")

#separations of concerns: ICCVScraper is only responsible for scraping papers from ICCV
class ICCVScraper(Scraper):
    def __init__(self, fetcher, num_papers_to_scrape=None):
        self.fetcher = fetcher
        self.num_papers_to_scrape = num_papers_to_scrape

    #when called on an instance of ICCVScraper will use fetcher attribute + num of papers to scrape papers from the provided url
    def get_publications(self, url):
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        papers = []

        arxiv_anchors = [anchor for anchor in soup.find_all('a') if 'arXiv' in anchor.text]

        # If num_papers_to_scrape is defined, limit the number of papers
        if self.num_papers_to_scrape:
            arxiv_anchors = arxiv_anchors[:self.num_papers_to_scrape]

        for anchor in arxiv_anchors:
            title = anchor.find_previous('dt').text.strip()
            link = anchor['href']

            arxiv_id = link.split('/')[-1]

            abstract, content = self.fetcher.fetch(arxiv_id)
            papers.append({'title': title, 'url': link, 'abstract': abstract, 'content': content})

        return papers