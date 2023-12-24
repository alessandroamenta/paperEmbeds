import logging

from bs4 import BeautifulSoup
import requests


class Scraper:
    def get_publications(self, url):
        raise NotImplementedError("Subclasses must implement this method!")
#an attribute is a variable that belongs to an object/instance of the class -> num_papers_to_scrape is an attribute that stores data
#bundle together related methods and variables/data they need to work on -> encapsulation

#separations of concerns: ICCVScraper is only responsible for scraping papers from ICCV
class ICCVScraper(Scraper):
    #initialize the object with fetcher and provided num of papers to scrape
    def __init__(self, fetcher, num_papers_to_scrape=None):
        #attribute with an instance of the fetcher object - it has data about which fetcher to use
        #dependency injection: when we create an instance of ICCVScraper, we pass it the fetcher it should use -> maybe we can make this dynamic?
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