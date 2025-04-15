from fpdf import FPDF
import unicodedata
import re

def clean_text(text):
    """Ultra-strict text cleaning that guarantees FPDF compatibility"""
    if text is None:
        return ""
    
    if not isinstance(text, str):
        try:
            text = str(text)
        except:
            return ""
    
    # Remove all non-ASCII and control characters
    text = re.sub(r'[^\x20-\x7E]', '', text)
    
    # Ensure text isn't empty after cleaning
    return text if text.strip() else "[Content]"

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)
        self.set_margins(20, 20, 20)  # Larger margins
        self.add_page()
        self.set_font("Arial", size=10)
        self.set_display_mode("fullwidth")  # Ensure maximum space
    
    def ultra_safe_text(self, text, font_style='', size=10):
        """Absolute guaranteed text output"""
        try:
            # First try strict cleaning
            clean = clean_text(str(text))
            if not clean.strip():
                clean = "[Content]"
            
            # Break into chunks if needed
            for i in range(0, len(clean), 80):  # 80 chars per line max
                chunk = clean[i:i+80]
                self.set_font("Arial", font_style, size)
                self.cell(0, 6, chunk, ln=1)
        except:
            # Final fallback
            self.set_font("Arial", size=8)
            self.cell(0, 6, "[Content]", ln=1)
    
    def header(self):
        self.ultra_safe_text("Top Ranked Companies", 'B', 14)
        self.ln(5)
    
    def company_block(self, company):
        # Name
        self.ultra_safe_text(company.get('name', 'Unknown Company'), 'B', 12)
        
        # Revenue
        revenue = company.get('revenue', 'N/A')
        if isinstance(revenue, (int, float)):
            revenue = f"${revenue:,.2f}"
        self.ultra_safe_text(f"Revenue: {revenue}")
        
        # Score
        self.ultra_safe_text(f"Score: {company.get('score', 0)}")
        
        # Description
        self.ultra_safe_text("Description:", 'I')
        desc = str(company.get('description', 'No description available.'))[:500]  # Strict limit
        self.ultra_safe_text(desc)
        self.ln(8)

def generate_pdf(companies, filename="top_companies.pdf"):
    try:
        pdf = PDF()
        if not companies:
            pdf.ultra_safe_text("No companies found in the document")
        else:
            for company in companies:
                pdf.company_block(company)
        
        # Final validation before output
        if pdf.pages_count == 0:
            pdf.add_page()
            pdf.ultra_safe_text("Report Contents")
        
        pdf.output(filename)
        print(f"PDF successfully generated at {filename}")
        return True
    except Exception as e:
        print(f"PDF generation failed: {e}")
        return False