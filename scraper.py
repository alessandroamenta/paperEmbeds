import os
import requests

import pandas as pd
from bs4 import BeautifulSoup

import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_abstract_from_arxiv(arxiv_id):
    api_url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error("Failed to fetch abstract for arXiv ID %s: %s", arxiv_id, e)
        return None

    soup = BeautifulSoup(response.content, 'xml')
    entry = soup.find('entry')
    abstract = entry.find('summary').text.strip()

    logger.debug("Fetched abstract for arXiv ID %s", arxiv_id)
    return abstract

def scrape_arxiv_papers(url, existing_papers=None):
    if existing_papers is None:
        existing_papers = {}

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error("Failed to scrape arXiv papers from URL %s: %s", url, e)
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    papers = []

    arxiv_anchors = [anchor for anchor in soup.find_all('a') if 'arXiv' in anchor.text]
    logger.info("Found %d arXiv anchors in URL %s", len(arxiv_anchors), url)

    for anchor in arxiv_anchors:
        title = anchor.find_previous('dt').text.strip()
        link = anchor['href']
        arxiv_id = link.split('/')[-1]

        if arxiv_id not in existing_papers:
            abstract = get_abstract_from_arxiv(arxiv_id)
            if abstract:  # Ensure abstract was successfully fetched
                papers.append({'title': title, 'url': link, 'abstract': abstract, 'arxiv_id': arxiv_id})

    return papers

def read_existing_papers(file_path):
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            logger.info("Existing papers read from '%s'", file_path)
            return df.set_index('arxiv_id').to_dict('index')
        except Exception as e:
            logger.error("Error reading existing papers from '%s': %s", file_path, e)
            return {}
    else:
        logger.info("No existing papers file found at '%s'. Starting fresh.", file_path)
        return {}

def main():
    file_path = 'papers_with_abstracts.csv'
    existing_papers = read_existing_papers(file_path)

    url = "https://openaccess.thecvf.com/ICCV2023?day=all"
    new_papers = scrape_arxiv_papers(url, existing_papers)

    if new_papers:
        df = pd.DataFrame(new_papers)
        df.to_csv(file_path, mode='a', header=not os.path.exists(file_path), index=False)
        logger.info("Added %d new papers to '%s'", len(new_papers), file_path)
    else:
        logger.info("No new papers found.")

if __name__ == '__main__':
    main()
