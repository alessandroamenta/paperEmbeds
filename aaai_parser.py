import pdfplumber
import logging
import re

logging.basicConfig(level=logging.INFO)

class AAAIParser:
    def __init__(self):
        self.expecting_title = True  # Start with expecting a title

    def get_publications(self, pdf_path):
        publications = []
        with pdfplumber.open(pdf_path) as pdf:
            # Process only the first page for demonstration purposes
            first_page = pdf.pages[0]
            logging.info('Processing page 1')
            text = first_page.extract_text()
            if text:
                page_publications = self.extract_publications_from_page(text)
                publications.extend(page_publications)
        logging.info('Completed parsing the first page of PDF')
        return publications

    def extract_publications_from_page(self, text):
        # Parse the page to get entries
        return self.parse_entries(text)

    def parse_entries(self, text):
        entries = []
        title = ""
        authors = []
        lines = text.split('\n')
        for line in lines:
            if self.expecting_title:
                if not line.strip().startswith('AAAI') and not line.strip().startswith('Title'):
                    title = line.strip()
                    self.expecting_title = False  # Next line(s) should be authors
            else:
                # Check if the line starts with a letter (author line) or a digit (next title)
                if re.match(r'^[A-Za-z]', line):
                    authors.append(line.strip())
                else:
                    # Process the current entry
                    if title and authors:
                        entries.append(self.process_entry(title, authors))
                    # Reset for next entry
                    title = ""
                    authors = []
                    self.expecting_title = True
        # Process the last entry if there is one
        if title and authors:
            entries.append(self.process_entry(title, authors))

        return entries

    def process_entry(self, title, authors_lines):
        authors_text = ' '.join(authors_lines)
        # Replace multiple spaces with a single space and split authors by semicolon
        authors = re.split(r';\s*', authors_text.strip())
        authors = [author.strip() for author in authors if author.strip()]
        return {'title': title, 'authors': authors}

# Usage example
pdf_path = './AAAI_Main-Track_2023-12-27.pdf'  # Update this path to the actual location of your PDF
parser = AAAIParser()
publications = parser.get_publications(pdf_path)

# Print the first few entries to verify the parsing
for publication in publications[:10]:  # Limit to first 10 for quick checking
    print(publication)

