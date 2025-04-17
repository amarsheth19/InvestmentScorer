# import requests
# from bs4 import BeautifulSoup
# import re
# import time

# def estimate_revenue_from_headcount(employees, industry):
#     """
#     Estimate revenue based on employee count and industry averages
#     Sources: https://www.quora.com/What-is-the-average-revenue-per-employee-by-industry
#     """
#     industry_multipliers = {
#         'software': 250000,
#         'tech': 200000,
#         'manufacturing': 150000,
#         'financial': 300000,
#         'default': 180000
#     }
    
#     multiplier = industry_multipliers.get(industry.lower(), industry_multipliers['default'])
#     return int(employees * multiplier)
 
# def scrape_linkedin_headcount(company_name):
#     """Mock LinkedIn scraper - in production use LinkedIn API or scraping service"""
#     try:
#         # This is a mock implementation - replace with real scraping code
#         time.sleep(1)  # Rate limiting
        
#         # Mock data - different headcounts based on company name keywords
#         if 'data' in company_name.lower():
#             return 150  # Data companies tend to be midsize
#         elif 'tech' in company_name.lower():
#             return 300
#         elif 'software' in company_name.lower():
#             return 200
#         else:
#             return 100  # Default for other industries
#     except:
#         return None

# def enrich_company_data(company):
#     try:
#         # Get headcount estimate
#         employees = scrape_linkedin_headcount(company['name'])
#         company['employees'] = employees or 100  # Default to 100 if scraping fails
        
#         # Estimate revenue if missing
#         if not company.get('revenue') or company['revenue'] == 0:
#             industry = 'software' if 'software' in company['description'].lower() else 'tech'
#             company['revenue'] = estimate_revenue_from_headcount(company['employees'], industry)
#             company['revenue_estimated'] = True
        
#         # Add AI/Tech scores
#         desc = company.get("description", "").lower()
#         company['ai_score'] = 3 if "ai" in desc or "artificial intelligence" in desc else 0
#         company['tech_score'] = 2 if "platform" in desc or "tech" in desc else 1
        
#         return company
#     except Exception as e:
#         print(f"Error enriching {company.get('name')}: {e}")
#         return company



def estimate_revenue_from_headcount(employees, industry):
    """Fast revenue estimation without API calls"""
    # Industry multipliers ($ revenue per employee)
    multipliers = {
        'software': 250000,
        'tech': 200000,
        'financial': 300000,
        'default': 180000
    }
    return employees * multipliers.get(industry.lower(), multipliers['default'])

def enrich_company_data(company):
    """Fast enrichment without real scraping"""
    try:
        # Estimate employees based on simple rules (no API calls)
        name = company['name'].lower()
        desc = company.get('description', '').lower()
        
        if 'data' in name or 'data' in desc:
            employees = 150
            industry = 'tech'
        elif 'tech' in name or 'software' in name:
            employees = 200
            industry = 'software'
        else:
            employees = 100
            industry = 'default'
        
        company['employees'] = employees
        
        # Estimate revenue if missing
        if not company.get('revenue') or company['revenue'] == 0:
            company['revenue'] = estimate_revenue_from_headcount(employees, industry)
            company['revenue_estimated'] = True
        
        return company
    except Exception as e:
        print(f"Skipping enrichment for {company.get('name')}: {str(e)}")
        return company