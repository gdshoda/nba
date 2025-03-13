import requests
import fitz  # PyMuPDF
from io import BytesIO

# URL of the hosted PDF
pdf_url = "https://ak-static.cms.nba.com/referee/injury/Injury-Report_2024-11-08_12AM.pdf"

# Download the PDF
response = requests.get(pdf_url)
response.raise_for_status()

# Open the PDF with PyMuPDF
pdf_document = fitz.open(stream=BytesIO(response.content), filetype="pdf")

# Extract text from each page
for page in pdf_document:
    text = page.get_text()
    tabs = page.find_tables()
    print(text)  # Print extracted text