import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def parse_companies(text):
    # Very basic parser using "Company Description" as an anchor
    sections = text.split("Company Description")
    companies = []
    for sec in sections[1:]:
        lines = sec.strip().split("\n")
        name = lines[0].strip()
        description = " ".join(lines[1:6])  # Approximate block
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
    if "AI" in company["description"]:
        score += ai_weight
    if "Platform" in company["description"] or "Tech" in company["description"]:
        score += platform_weight
    if 5_000_000 <= company["revenue"] <= 30_000_000:
        score += revenue_weight
    return score

def get_top_10(companies, ai_weight=1, platform_weight=1, revenue_weight=1):
    for c in companies:
        c["score"] = score_company(c, ai_weight, platform_weight, revenue_weight)
    return sorted(companies, key=lambda x: x["score"], reverse=True)[:10]


# import fitz  # PyMuPDF
# import re

# def extract_text_from_pdf(pdf_path):
#     try:
#         doc = fitz.open(pdf_path)
#         text = ""
#         for page in doc:
#             text += page.get_text()
#         return text
#     except Exception as e:
#         raise Exception(f"Failed to extract text from PDF: {str(e)}")

# def parse_companies(text):
#     companies = []
#     sections = re.split(r'Company\s*Description|Company\s*Profile|Company\s*Overview', text, flags=re.IGNORECASE)
    
#     for sec in sections[1:]:
#         lines = [line.strip() for line in sec.split('\n') if line.strip()]
#         if not lines:
#             continue
            
#         name = lines[0]
#         description = " ".join(lines[1:min(10, len(lines))])
        
#         revenue = None
#         revenue_pattern = r'Revenue:\s*\$?(\d+(?:,\d+)*(?:\.\d+)?)\s*[MB]?'
#         for line in lines:
#             match = re.search(revenue_pattern, line, re.IGNORECASE)
#             if match:
#                 try:
#                     revenue_str = match.group(1).replace(',', '')
#                     if 'M' in line.upper():
#                         revenue = float(revenue_str) * 1_000_000
#                     elif 'B' in line.upper():
#                         revenue = float(revenue_str) * 1_000_000_000
#                     else:
#                         revenue = float(revenue_str)
#                     break
#                 except:
#                     continue

#         companies.append({
#             "name": name,
#             "description": description,
#             "revenue": revenue or 0
#         })
    
#     return companies

# def score_company(company, ai_weight, platform_weight, revenue_weight):
#     score = 0
    
#     if "AI" in company["description"].upper() or "artificial intelligence" in company["description"].upper():
#         score += ai_weight * 2
    
#     if "platform" in company["description"].lower() or "tech" in company["description"].lower():
#         score += platform_weight
    
#     if company["revenue"]:
#         if 5_000_000 <= company["revenue"] <= 30_000_000:
#             score += revenue_weight * 2
#         elif company["revenue"] > 30_000_000:
#             score += revenue_weight * 0.5
#         else:
#             score += revenue_weight
    
#     return round(score, 2)

# def get_top_10(companies, ai_weight=1, platform_weight=1, revenue_weight=1):
#     for c in companies:
#         c["score"] = score_company(c, ai_weight, platform_weight, revenue_weight)
#     return sorted(companies, key=lambda x: x["score"], reverse=True)[:10]