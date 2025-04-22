# scraper.py
from industry_classifier import determine_industry

def estimate_revenue_from_industry(employees, industry):
    """Estimate revenue based on industry benchmarks per employee"""
    benchmarks = {
        'FinTech & Payments': 250000,          # $250K per employee
        'Enterprise Software': 220000,          # $220K per employee
        'Commerce Tech': 200000,                # $200K per employee
        'Communications & Digital Infrastructure': 180000,
        'HR Technology & Application Software': 175000,
        'Internet & Enabling Technologies': 160000,
        'Semiconductors & Related Technologies': 140000,
        'other': 150000
    }
    return int(employees * benchmarks.get(industry, 150000))

def estimate_ebitda_margin(industry):
    """Estimate typical EBITDA margin by industry"""
    margins = {
        'FinTech & Payments': 0.30,             # 30%
        'Enterprise Software': 0.35,            # 35%
        'Commerce Tech': 0.25,                 # 25%
        'Communications & Digital Infrastructure': 0.20,
        'HR Technology & Application Software': 0.25,
        'Internet & Enabling Technologies': 0.20,
        'Semiconductors & Related Technologies': 0.15,
        'other': 0.10
    }
    return margins.get(industry, 0.10)

def enrich_company_data(company):
    try:
        # Skip if already enriched
        if company.get('_enriched'):
            return company
            
        # Determine industry
        #industry = determine_industry(company.get('description', ''))
        #company['industry'] = industry
        industry = company['industry'][0]
        
        
        # Estimate employees if missing
        if not company.get('employees'):
            # Base estimation on description length and keywords
            desc = company.get('description', '').lower()
            base = 50
            if 'enterprise' in desc:
                base += 150
            if 'startup' in desc:
                base = max(10, base - 30)
            company['employees'] = base + (len(desc) // 100)
            company['employees_estimated'] = True
        
        # Estimate revenue if missing
        if not company.get('revenue'):
            company['revenue'] = estimate_revenue_from_industry(
                company['employees'],
                industry
            )
            company['revenue_estimated'] = True
        
        # Estimate EBITDA if missing
        if not company.get('ebitda') and company.get('revenue'):
            margin = estimate_ebitda_margin(industry)
            company['ebitda'] = int(company['revenue'] * margin)
            company['ebitda_estimated'] = True
        
        # Estimate growth if missing
        if not company.get('growth_rate'):
            company['growth_rate'] = {
                'fintech': 25,
                'software': 30,
                'data': 20,
                'security': 25,
                'infrastructure': 15,
                'hr_tech': 20,
                'hardware': 15,
                'real_estate': 10,
                'other': 10
            }.get(industry, 10)
            company['growth_estimated'] = True
        
        company['_enriched'] = True
        return company
    except Exception as e:
        print(f"Error enriching {company.get('name', 'Unknown')}: {str(e)}")
        return company