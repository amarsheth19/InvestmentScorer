from fpdf import FPDF
import re

def clean_text(text):
    if not text:
        return ""
    text = str(text)
    # Keep only printable ASCII and preserve line breaks
    text = re.sub(r'[^\x20-\x7E\r\n]', '', text)
    return text

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)
        self.set_margins(20, 20, 20)
        self.add_page()
        self.set_font("Arial", size=10)
    
    def safe_text(self, text, style='', size=10, max_len=None):
        self.set_font("Arial", style, size)
        text = clean_text(text)
        
        if max_len:
            text = text[:max_len] + '...' if len(text) > max_len else text
        
        # Split into paragraphs and handle each separately
        for paragraph in text.split('\n'):
            self.multi_cell(0, 6, paragraph)
            self.ln(2)
    
    def header(self):
        self.safe_text("Top Ranked Companies", 'B', 14)
        self.ln(5)

    def company_block(self, company):
        # Name and basic info
        self.safe_text(company.get('name', 'Unknown'), 'B', 12)
        self.safe_text(f"Score: {company.get('score', 0)}")
        
        # Revenue with estimation note if applicable
        revenue_text = f"Revenue: ${company.get('revenue', 0):,}"
        if company.get('revenue_estimated'):
            revenue_text += " (estimated from headcount)"
        self.safe_text(revenue_text)
        
        self.safe_text(f"Employees: {company.get('employees', 'N/A')}")
        
        # Full description with proper wrapping
        self.safe_text("Description:", 'I')
        self.safe_text(company.get('description', 'No description available'), max_len=2000)
        self.ln(10)

def generate_pdf(companies, filename="top_companies.pdf"):
    try:
        pdf = PDF()
        if not companies:
            pdf.safe_text("No companies found in the document")
        else:
            for company in companies:
                pdf.company_block(company)
        pdf.output(filename)
        return True
    except Exception as e:
        print(f"PDF generation error: {e}")
        return False