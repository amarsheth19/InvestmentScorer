import fitz  # PyMuPDF
import re
from industry_classifier import determine_industry

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using precise layout preservation"""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text("text", flags=fitz.TEXT_PRESERVE_LIGATURES | fitz.TEXT_PRESERVE_WHITESPACE)
    return text

def clean_company_name(name):
    """Clean and standardize company names"""
    if not name:
        return "Unknown Company"
    
    # Remove common prefixes/suffixes
    name = re.sub(r'^(Attendee\(s\)|Company\s*Description|Company\s*Profile|Software\s*Sector:)\s*', '', name, flags=re.IGNORECASE)
    name = re.sub(r'[-–].*$', '', name)  # Remove everything after hyphen/dash
    name = re.sub(r'\b(inc|llc|ltd|corp|corporation|plc|www\..*?)\b\.?$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'[^a-zA-Z0-9& ]', '', name)  # Remove special chars
    return name.strip()

def parse_companies(text):
    """Parse company data from PDF text with improved name extraction"""
    # Split by likely company sections (bold text at start of line)
    sections = re.split(r'\n(?=\*?[A-Z][a-zA-Z0-9& ]{2,})', text)
    companies = []
    
    for sec in sections[1:]:  # Skip first section
        lines = [line.strip() for line in sec.split('\n') if line.strip()]
        if not lines or len(lines) < 3:  # Skip very short sections
            continue
            
        # Extract company name (first line, clean bold markers)
        name = clean_company_name(lines[0].strip('*').strip())
        if not name or len(name.split()) > 6:  # Skip unlikely names
            continue
            
        # Get description from next non-empty lines
        description_lines = []
        for line in lines[1:]:
            if not re.match(r'^(Revenue|EBITDA|Growth|Employees|Ownership|Financial)', line, re.I):
                description_lines.append(line)
            else:
                break
        description = " ".join(description_lines[:5])  # First 5 description lines max
        
        # Extract financial metrics
        revenue = None
        ebitda = None
        growth = None
        employees = None
        
        for line in lines:
            # Revenue extraction
            if "Revenue" in line:
                try:
                    num = re.search(r'[\$£€]?(\d+\.?\d*)\s*[MB]', line.replace(',', ''))
                    if num:
                        revenue = float(num.group(1))
                        if 'M' in line.upper():
                            revenue *= 1_000_000
                        elif 'B' in line.upper():
                            revenue *= 1_000_000_000
                        revenue = int(revenue)
                except:
                    pass
            # EBITDA extraction
            elif "EBITDA" in line:
                try:
                    num = re.search(r'[\$£€]?(\d+\.?\d*)\s*[MB]', line.replace(',', ''))
                    if num:
                        ebitda = float(num.group(1))
                        if 'M' in line.upper():
                            ebitda *= 1_000_000
                        elif 'B' in line.upper():
                            ebitda *= 1_000_000_000
                        ebitda = int(ebitda)
                except:
                    pass
            # Growth rate extraction
            elif "Growth" in line or "growth" in line:
                try:
                    growth = int(re.search(r'(\d+)%', line).group(1))
                except:
                    pass
            # Employees extraction
            elif "employees" in line.lower() or "headcount" in line.lower():
                try:
                    employees = int(re.search(r'~?(\d+)', line).group(1))
                except:
                    pass

        companies.append({
            "name": name,
            "description": description,
            "revenue": revenue,
            "ebitda": ebitda,
            "growth_rate": growth,
            "employees": employees,
        })
    
    return companies

def score_company(company):
    """Score companies based on Strattam Capital's investment criteria"""
    score = 0
    
    # Revenue scoring (10-30M ideal) - 40 points max
    if company.get('revenue'):
        if 10_000_000 <= company['revenue'] <= 30_000_000:
            score += 40  # Perfect match
        elif 5_000_000 <= company['revenue'] < 10_000_000:
            score += 30  # Below ideal but acceptable
        elif 30_000_000 < company['revenue'] <= 50_000_000:
            score += 35  # Slightly above ideal
        elif company['revenue'] > 50_000_000:
            score += 20  # Too large
        else:
            score += 10  # Too small
    
    # Growth scoring (>10% ideal) - 30 points max
    if company.get('growth_rate'):
        if company['growth_rate'] >= 30:
            score += 30  # Exceptional growth
        elif company['growth_rate'] >= 20:
            score += 25  # Strong growth
        elif company['growth_rate'] >= 10:
            score += 20  # Meets minimum
        elif company['growth_rate'] >= 5:
            score += 10  # Below target
        else:
            score += 5   # Low growth
    
    # Profitability scoring - 20 points max
    if company.get('ebitda'):
        if company['ebitda'] > company.get('revenue', 1) * 0.2:  # >20% margin
            score += 20
        elif company['ebitda'] > 0:
            score += 15  # Positive but low margin
        else:
            score += 5   # Negative EBITDA
    
    # Industry fit scoring - 10 points max
    industry = determine_industry(company.get('description', ''))
    if industry in ['software', 'fintech', 'data', 'security']:
        score += 10  # Perfect match
    elif industry in ['infrastructure', 'hr_tech']:
        score += 5   # Partial match
    
    return score

def get_top_10(companies):
    """Rank companies and return top 10"""
    for c in companies:
        c['score'] = score_company(c)
        c['industry'] = determine_industry(c.get('description', ''))
    return sorted(companies, key=lambda x: x['score'], reverse=True)[:10]