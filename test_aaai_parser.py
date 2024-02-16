from aaai_parser import AAAIParser

# Path to the AAAI PDF file
pdf_path = './AAAI_Main-Track_2023-12-27.pdf'

# Create an instance of AAAIParser and parse the PDF
parser = AAAIParser()
publications = parser.get_publications(pdf_path)

# Quick check
print(publications[:10])  
