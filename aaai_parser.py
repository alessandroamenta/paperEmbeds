import pdfplumber
import logging
import re

logging.basicConfig(level=logging.DEBUG, filename='parser.log', filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')

class AAAIParser:
    def __init__(self):
        pass

    def get_publications(self, pdf_path):
        publications = []
        with pdfplumber.open(pdf_path) as pdf:
            for page_number, page in enumerate(pdf.pages):
                logging.info(f'Processing page {page_number + 1}')
                text = page.extract_text()
                if text:
                    page_publications = self.extract_publications_from_page(text)
                    publications.extend(page_publications)
        logging.info('Completed parsing PDF')
        return publications

    def extract_publications_from_page(self, text):
        # Parse the page to get entries
        return self.parse_entries(text)

    def parse_entries(self, text):
        entries = []
        entry_lines = []
        lines = text.split('\n')
        for line in lines[2:]:  # Skip the header lines
            if re.match(r'^\d+\s', line):  # New entry starts
                if entry_lines:  # Previous entry exists
                    entries.append(self.process_entry_lines(entry_lines))
                    entry_lines = []  # Reset for the next entry
            entry_lines.append(line)
        if entry_lines:  # Add the last entry if there is one
            entries.append(self.process_entry_lines(entry_lines))
        return entries

    def process_entry_lines(self, entry_lines):
        entry_text = ' '.join(entry_lines)  # Combine lines to handle multi-line entries
        id_match = re.match(r'^(\d+)', entry_text)
        if not id_match:
            logging.warning('No ID found in entry: ' + ' '.join(entry_lines))
            return None
        id_ = id_match.group(1)
        title_authors = entry_text[len(id_):].strip()  # Remove ID from the start
        first_semicolon_idx = title_authors.find(';')
        title = title_authors[:first_semicolon_idx].strip()
        authors = title_authors[first_semicolon_idx+1:].strip().split(';')
        authors = [author.strip() for author in authors if author.strip()]  # Clean up author names
        return {'id': id_, 'title': title, 'authors': authors}

# Usage example
pdf_path = 'AAAI_Main-Track_2024-01-04.pdf'  # Update this path to the actual location of your PDF
parser = AAAIParser()
publications = parser.get_publications(pdf_path)

# Print the first few entries to verify the parsing
for publication in publications[:10]:
    print(publication)
