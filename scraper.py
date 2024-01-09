import os
import requests

from bs4 import BeautifulSoup
import pandas as pd

# import PyPDF2  # Not needed if only fetching abstracts
# from io import BytesIO  # Not needed if only fetching abstracts

def get_abstract_from_arxiv(arxiv_id):
    # Base URL for the arXiv API
    api_url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
    
    response = requests.get(api_url)
    response.raise_for_status()
    
    # Parse the XML response
    soup = BeautifulSoup(response.content, 'xml')
    entry = soup.find('entry')
    abstract = entry.find('summary').text.strip()
    
    return abstract  # Only returning the abstract

def scrape_arxiv_papers(url, existing_papers=None):
    if existing_papers is None:
        existing_papers = {}

    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')
    papers = []
    
    arxiv_anchors = [anchor for anchor in soup.find_all('a') if 'arXiv' in anchor.text]
    
    for anchor in arxiv_anchors:
        title = anchor.find_previous('dt').text.strip()
        link = anchor['href']
        arxiv_id = link.split('/')[-1]

        # Check if paper already exists
        if arxiv_id not in existing_papers:
            abstract = get_abstract_from_arxiv(arxiv_id)
            papers.append({'title': title, 'url': link, 'abstract': abstract, 'arxiv_id': arxiv_id})

    return papers

def read_existing_papers(file_path):
    if os.path.exists(file_path):
        return pd.read_csv(file_path).set_index('arxiv_id').to_dict('index')
    return {}

# Main code
file_path = 'papers_with_abstracts.csv'
existing_papers = read_existing_papers(file_path)

url = "https://openaccess.thecvf.com/ICCV2023?day=all"
new_papers = scrape_arxiv_papers(url, existing_papers)

if new_papers:
    df = pd.DataFrame(new_papers)
    df.to_csv(file_path, mode='a', header=not os.path.exists(file_path), index=False)
    print(f"Added {len(new_papers)} new papers to '{file_path}'")
else:
    print("No new papers found.")

def main():
    file_path = 'papers_with_abstracts.csv'
    existing_papers = read_existing_papers(file_path)

    url = "https://openaccess.thecvf.com/ICCV2023?day=all"
    new_papers = scrape_arxiv_papers(url, existing_papers)

    if new_papers:
        df = pd.DataFrame(new_papers)
        df.to_csv(file_path, mode='a', header=not os.path.exists(file_path), index=False)
        print(f"Added {len(new_papers)} new papers to '{file_path}'")
    else:
        print("No new papers found.")

if __name__ == '__main__':
    main()

#all in one script
#scraping and fetching are intertwined -> changing how we fetch from arxiv would also mean changing how we scrape iccv
#not that flexible -> to adapt to another conference or fetch from a different source like google scholar we'd need to change the whole thing

#new version with OOP
#divided in classes, each focused on a task -> fetching, scraping
#the scraper is independent of the fetcher
#can easely add new fetchers or scrapers without messing up existing code