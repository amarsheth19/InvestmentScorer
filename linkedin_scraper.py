from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

def setup_driver():
    options = Options()
    options.add_argument("--headless")  # Run in background
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def scrape_linkedin(company_name):
    driver = setup_driver()
    try:
        # Search for company
        search_url = f"https://www.linkedin.com/search/results/companies/?keywords={company_name.replace(' ', '%20')}"
        driver.get(search_url)
        
        # Wait for results and click first result
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".entity-result__title-text a"))
        ).click()
        
        # Wait for company page to load
        time.sleep(random.uniform(2, 4))
        
        # Try to get headcount
        try:
            about_section = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".org-page-details__definition-text"))
            )
            employees_text = about_section.text
            if 'employees' in employees_text.lower():
                return int(employees_text.split()[0].replace(',', ''))
        except:
            pass
        
        # Alternative method - look in the "About" section
        try:
            driver.find_element(By.CSS_SELECTOR, "[data-control-name='about_tab']").click()
            time.sleep(1)
            about_text = driver.find_element(By.CSS_SELECTOR, ".org-about-us-organization-description__text").text
            match = re.search(r'(\d+,?\d*)\s+employees', about_text, re.IGNORECASE)
            if match:
                return int(match.group(1).replace(',', ''))
        except:
            pass
        
        return None
    except Exception as e:
        print(f"Error scraping LinkedIn for {company_name}: {str(e)}")
        return None
    finally:
        driver.quit()

def estimate_revenue_from_linkedin(company_name):
    """Actual implementation using scraping"""
    employees = scrape_linkedin(company_name)
    if employees is None:
        return None
        
    # Industry-specific revenue per employee estimates
    benchmarks = {
        'software': 250000,
        'fintech': 300000,
        'manufacturing': 150000,
        'retail': 100000,
        'other': 200000
    }
    
    # Default to software if we don't know industry
    return employees * benchmarks.get('software', 200000)