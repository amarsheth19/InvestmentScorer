import fitz  # PyMuPDF
import re

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def parse_companies(text):
    sections = re.split(r'Company\s*Description|Company\s*Profile', text, flags=re.IGNORECASE)
    companies = []
    
    for sec in sections[1:]:
        lines = [line.strip() for line in sec.split('\n') if line.strip()]
        if not lines:
            continue
            
        name = lines[0]
        description = " ".join(lines[1:6])
        revenue = None
        
        for line in lines:
            if "Revenue" in line:
                try:
                    revenue = int(line.replace("Revenue:", "").replace("$", "").replace("M", "").strip()) * 1_000_000
                except:
                    pass

        companies.append({
            "name": name,
            "description": description,
            "revenue": revenue or 0,
        })
    
    return companies

def score_company(company, ai_weight, platform_weight, revenue_weight):
    score = 0
    if "AI" in company["description"].upper():
        score += ai_weight * 2
    if "platform" in company["description"].lower() or "tech" in company["description"].lower():
        score += platform_weight
    if 5_000_000 <= company["revenue"] <= 30_000_000:
        score += revenue_weight * 2
    elif company["revenue"] > 0:
        score += revenue_weight
    return score

def get_top_10(companies, ai_weight=1, platform_weight=1, revenue_weight=1):
    for c in companies:
        c["score"] = score_company(c, ai_weight, platform_weight, revenue_weight)
    return sorted(companies, key=lambda x: x["score"], reverse=True)[:10]