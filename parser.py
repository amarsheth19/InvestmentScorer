import fitz  # PyMuPDF
import re


VALID_INDUSTRIES = [
    "Commerce Tech", "FinTech & Payments", "Communications & Digital Infrastructure",
    "Enterprise Software", "HR Technology & Application Software", "Internet & Enabling Technologies", "Semiconductors & Related Technologies"
]

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF while skipping first 2 pages (TOC)"""
    doc = fitz.open(pdf_path)
    text = ""

    # Start from page 2
    for page in doc[1:]:
        text += page.get_text("text", flags=fitz.TEXT_PRESERVE_LIGATURES | fitz.TEXT_PRESERVE_WHITESPACE)
        text += "\n===== PAGE END =====\n" 
    return text

def clean_company_name(name):
    """Clean and standardize company names"""
    if not name:
        return "Unknown Company"
    name = re.sub(r'www\..+', '', name) 
    name = re.sub(r'\s+', ' ', name).strip()  
    return name

def parse_companies(text):
    """Parse company data from PDF text using 5th line rule"""
    companies = []
    pages = text.split('===== PAGE END =====')

    for page in pages:
        lines = [line.strip() for line in page.split('\n') if line.strip()]
        if len(lines) < 5:  # Skip pages without enough lines
            continue

        # 5th line contains company name (0-indexed line 4)
        name = clean_company_name(lines[4])
        if not name:
            continue

        # Find the Company Description section
        description = ""
        desc_start = None
        for i, line in enumerate(lines):
            if "Company Description" in line:
                desc_start = i + 1
                break

        if desc_start:
            # Collect description lines until next section
            desc_lines = []
            for line in lines[desc_start:]:
                if re.match(r'^(Company Highlights|Growth Opportunities|Financial Highlights|Ownership Today|Public Company Comps)', line):
                    break
                desc_lines.append(line)
            description = " ".join(desc_lines)

        # Extract financial metrics
        revenue = None
        ebitda = None
        growth = None
        employees = None

        # Search the entire page content for financial data
        page_text = "\n".join(lines)

        # Revenue extraction
        rev_match = re.search(r'Revenue[:\s]*[\$£€]?(\d+\.?\d*)\s*([MBmb])', page_text, re.IGNORECASE)
        if rev_match:
            try:
                revenue = float(rev_match.group(1))
                if 'm' in rev_match.group(2).lower():
                    revenue *= 1_000_000
                elif 'b' in rev_match.group(2).lower():
                    revenue *= 1_000_000_000
                revenue = int(revenue)
            except:
                pass

        # EBITDA extraction
        ebitda_match = re.search(r'EBITDA[:\s]*[\$£€]?(\d+\.?\d*)\s*([MBmb])', page_text, re.IGNORECASE)
        if ebitda_match:
            try:
                ebitda = float(ebitda_match.group(1))
                if 'm' in ebitda_match.group(2).lower():
                    ebitda *= 1_000_000
                elif 'b' in ebitda_match.group(2).lower():
                    ebitda *= 1_000_000_000
                ebitda = int(ebitda)
            except:
                pass

        # Growth rate extraction
        growth_match = re.search(r'(?:Growth|Growth Rate)[:\s]*(\d+)%', page_text, re.IGNORECASE)
        if growth_match:
            try:
                growth = int(growth_match.group(1))
            except:
                pass

        # Employee extraction
        emp_match = re.search(r'(?:Employees|Headcount)[:\s]*~?(\d+)', page_text, re.IGNORECASE)
        if emp_match:
            try:
                employees = int(emp_match.group(1))
            except:
                pass

        # If not found in dedicated field, try extracting from description
        if employees is None and description:
            employees_match = re.search(r'(?:with|has|employs)\s*(?:~)?(\d+)\s*employees', description, re.IGNORECASE)
            if employees_match:
                try:
                    employees = int(employees_match.group(1))
                except:
                    pass

        # Extract Industry
        industry = extract_industry(page_text)

        companies.append({
            "name": name,
            "description": description,
            "revenue": revenue,
            "ebitda": ebitda,
            "growth_rate": growth,
            "employees": employees,
            "industry": industry  # Add extracted industry to company data
        })

    return companies

def score_company(company, weights):
    """Score companies based on customizable weightings"""
    score = 0

    # Get weights with defaults if not provided
    revenue_weight = weights.get('revenue_weight', 1)
    growth_weight = weights.get('growth_weight', 1)
    profitability_weight = weights.get('profitability_weight', 1)
    industry_weight = weights.get('industry_weight', 1)
    size_weight = weights.get('size_weight', 1)
    selected_industries = weights.get('selected_industries', [])  # Get selected industries

    # Revenue scoring (10-30M ideal) - max 40 points
    revenue = company.get('revenue')
    if revenue:
        if 10_000_000 <= revenue <= 30_000_000:
            score += 40 * revenue_weight
        elif 5_000_000 <= revenue < 10_000_000:
            score += 30 * revenue_weight
        elif 30_000_000 < revenue <= 50_000_000:
            score += 25 * revenue_weight
        elif revenue > 50_000_000:
            score += 10 * revenue_weight
        else:
            score += 5 * revenue_weight

    # Growth scoring (>10% ideal) - max 30 points
    growth = company.get('growth_rate')
    if growth:
        if growth >= 30:
            score += 30 * growth_weight
        elif growth >= 20:
            score += 25 * growth_weight
        elif growth >= 10:
            score += 20 * growth_weight
        elif growth >= 5:
            score += 10 * growth_weight
        else:
            score += 5 * growth_weight

    # Profitability scoring - max 20 points
    ebitda = company.get('ebitda')
    revenue = company.get('revenue', 1)
    if ebitda:
        if ebitda > revenue * 0.2:  # >20% margin
            score += 20 * profitability_weight
        elif ebitda > 0:
            score += 15 * profitability_weight
        else:
            score += 5 * profitability_weight

    # Industry fit scoring - max 10 points
    industry = company.get('industry')
    if industry and selected_industries:
        # Check if any of the company's industries are in the selected industries
        company_industries = industry if isinstance(industry, list) else [industry]
        matched_industries = [ind for ind in company_industries if ind in selected_industries]
        
        if matched_industries:
            # Prioritize certain industries with higher scores
            if any("Enterprise Software" in ind for ind in matched_industries):
                score += 10 * industry_weight
            elif any("FinTech" in ind for ind in matched_industries):
                score += 8 * industry_weight
            elif any("Software" in ind for ind in matched_industries):
                score += 6 * industry_weight
            else:
                # Basic match with selected industries
                score += 5 * industry_weight

    # Company size scoring - max 10 points
    employees = company.get('employees')
    if employees:
        if 50 <= employees <= 200:
            score += 10 * size_weight
        elif employees < 50:
            score += 5 * size_weight
        else:
            score += 2 * size_weight

    # Normalize the score to a 100-point scale based on weights
    max_possible = (
        40 * revenue_weight +
        30 * growth_weight +
        20 * profitability_weight +
        10 * industry_weight +
        10 * size_weight
    )

    if max_possible > 0:
        normalized_score = (score / max_possible) * 100
        return round(normalized_score, 2)
    return 0

def get_top_10(companies, weights=None):
    """Rank companies and return top 10 with customizable weights"""
    # Default weights if none provided
    if weights is None:
        weights = {
            'revenue_weight': 1,
            'growth_weight': 1,
            'profitability_weight': 1,
            'industry_weight': 1,
            'size_weight': 1
        }

    for c in companies:
        c['score'] = score_company(c, weights)  # Pass weights to score_company
        # Debug print
        print(f"Company: {c['name']}")
        print(f"Revenue: {c.get('revenue')}")
        print(f"Growth: {c.get('growth_rate')}")
        print(f"EBITDA: {c.get('ebitda')}")
        print(f"Industry: {c.get('industry')}")
        print(f"Score: {c['score']}\n")

    return sorted(companies, key=lambda x: x['score'], reverse=True)[:10]

def extract_industry(text):
    """
    Extract industry from PDF based on predefined valid industries.
    """
    found_industries = []
    for industry in VALID_INDUSTRIES:
        if re.search(re.escape(industry), text, re.IGNORECASE):
            found_industries.append(industry)
    if not found_industries:
        found_industries.append("Semiconductors & Related Technologies")

    return found_industries