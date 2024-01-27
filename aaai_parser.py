import PyPDF2
from scrapers import Scraper
import re

class AAAIParser(Scraper):
    def __init__(self):
        super().__init__()

    def get_publications(self, pdf_path):
        publications = []
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text = page.extract_text()
                publications.extend(self.extract_publications_from_page(text))
        return publications

    def extract_publications_from_page(self, text):
        # Regex pattern to match the structure: ID Title Authors
        pattern = r'(\d+)\n(.*?)\n(.*?)(?=\n\d+\n|\Z)'
        matches = re.findall(pattern, text, re.DOTALL)
        publications = [{'id': match[0], 'title': match[1], 'authors': match[2]} for match in matches]
        return publications
