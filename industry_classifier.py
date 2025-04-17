# industry_classifier.py
def determine_industry(description):
    """Classify company into industry based on description"""
    if not description:
        return 'other'
    
    desc = description.lower()
    
    if any(word in desc for word in ['fintech', 'financial', 'payment', 'banking', 'wealth']):
        return 'fintech'
    elif any(word in desc for word in ['software', 'saas', 'platform', 'devops']):
        return 'software'
    elif any(word in desc for word in ['data', 'analytics', 'database', 'time-series']):
        return 'data'
    elif any(word in desc for word in ['security', 'cyber', 'authentication', 'identity']):
        return 'security'
    elif any(word in desc for word in ['cloud', 'hosting', 'colocation', 'data center']):
        return 'infrastructure'
    elif any(word in desc for word in ['construction', 'real estate', 'property']):
        return 'real_estate'
    elif any(word in desc for word in ['drone', 'robotics', 'iot']):
        return 'hardware'
    elif any(word in desc for word in ['hr', 'talent', 'employee', 'workforce']):
        return 'hr_tech'
    else:
        return 'other'