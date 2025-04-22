from fpdf import FPDF
import re

def clean_text(text):
    """Sanitize text for PDF output with proper encoding"""
    if not text:
        return ""
    text = str(text)
    # Replace problematic characters and preserve line breaks
    text = text.replace('\u2022', '-')  # Replace bullet with hyphen
    text = re.sub(r'[^\x20-\x7E\r\n]', '', text)  # Remove non-ASCII
    text = re.sub(r' +', ' ', text)  # Collapse multiple spaces
    return text.strip()

def clean_company_name(raw_name):
    """Clean the company name while preserving its structure"""
    if not raw_name:
        return "Unknown Company"
    
    # Remove any score/industry markers that might have been added
    name = re.sub(r'\s*[|-].*$', '', raw_name)
    
    # Remove common unwanted prefixes but preserve the rest
    name = re.sub(r'^(Company|Profile|Description):?\s*', '', name, flags=re.IGNORECASE)
    
    # Clean up any remaining special characters except basic punctuation
    name = re.sub(r'[^a-zA-Z0-9& \-\'\.]', '', name)
    
    # Collapse multiple spaces and trim
    name = re.sub(r'\s+', ' ', name).strip()
    
    # Capitalize properly (optional)
    # name = name.title()
    
    return name if name else "Unknown Company"

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)
        self.set_margins(20, 20, 20)
        self.header_printed = False
        self.add_page()
        self.set_font("Arial", size=10)
    
    def header(self):
        """Only print header on first page"""
        if not self.header_printed:
            self.set_font("Arial", 'B', 14)
            self.cell(0, 10, "Top Companies for Strattam Capital", 0, 1, 'C')
            self.set_font("Arial", 'I', 10)
            self.cell(0, 6, "Investment Criteria: $10-30M revenue, >10% growth, positive EBITDA", 0, 1, 'C')
            self.ln(10)
            self.header_printed = True
    
    def safe_text(self, text, style='', size=10):
        """Safe text output with encoding handling"""
        text = clean_text(text)
        self.set_font("Arial", style, size)
        self.multi_cell(0, 6, text)
        self.ln(2)
    
    def company_block(self, company):
        """Format a company entry in the PDF with proper name handling"""
        # Get and clean the company name
        raw_name = company.get('name', '')
        clean_name = clean_company_name(raw_name)
        
        # Company name as title
        self.set_font("Arial", 'B', 12)
        self.cell(0, 8, clean_name, 0, 1, 'L')
        self.ln(2)
        
        # Score and industry as simple bullets
        self.set_font("Arial", '', 10)
        self.cell(0, 6, f"- Score: {company.get('score', 0)}", 0, 1)
        self.cell(0, 6, f"- Industry: {company.get('industry', ['N/A'])[0]}", 0, 1)
        self.ln(2)
        
        # Financial metrics with simple bullets
        revenue_text = f"- Revenue: ${company.get('revenue', 0):,}"
        if company.get('revenue_estimated'):
            revenue_text += " (estimated)"
        self.cell(0, 6, revenue_text, 0, 1)
        
        ebitda_text = f"- EBITDA: ${company.get('ebitda', 0):,}"
        if company.get('ebitda_estimated'):
            ebitda_text += " (estimated)"
        self.cell(0, 6, ebitda_text, 0, 1)
        
        self.cell(0, 6, f"- Growth Rate: {company.get('growth_rate', 'N/A')}%", 0, 1)
        self.cell(0, 6, f"- Employees: {company.get('employees', 'N/A')}", 0, 1)
        self.ln(2)
        
        # Description
        self.set_font("Arial", 'I', 10)
        self.cell(0, 6, "Description:", 0, 1)
        self.set_font("Arial", '', 10)
        self.safe_text(company.get('description', 'No description available'))
        
        # Separator
        self.ln(8)
        self.cell(0, 0, '', 'T')
        self.ln(10)

def generate_pdf(companies, filename="top_companies.pdf"):
    """Generate the final PDF report"""
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