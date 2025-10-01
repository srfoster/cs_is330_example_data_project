"""
Olympic College Course Prefix Scraper
Simple script to extract all course prefixes from the catalog
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import logging

def setup_driver(headless=False):
    """Initialize Chrome WebDriver"""
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def extract_course_prefixes():
    """Extract course prefixes from Olympic College catalog"""
    
    # Direct URL to Olympic College course catalog
    url = "https://csprd.ctclink.us/psp/csprd/EMPLOYEE/SA/s/WEBLIB_HCX_CM.H_COURSE_CATALOG.FieldFormula.IScript_Main?institution=WA030&PortalActualURL=https%3a%2f%2fcsprd.ctclink.us%2fpsc%2fcsprd%2fEMPLOYEE%2fSA%2fs%2fWEBLIB_HCX_CM.H_COURSE_CATALOG.FieldFormula.IScript_Main&PortalContentURL=https%3a%2f%2fcsprd.ctclink.us%2fpsc%2fcsprd%2fEMPLOYEE%2fSA%2fs%2fWEBLIB_HCX_CM.H_COURSE_CATALOG.FieldFormula.IScript_Main&PortalContentProvider=SA&PortalCRefLabel=Course%20Catalog&PortalRegistryName=EMPLOYEE&PortalServletURI=https%3a%2f%2fcsprd.ctclink.us%2fpsp%2fcsprd%2f&PortalURI=https%3a%2f%2fcsprd.ctclink.us%2fpsc%2fcsprd%2f&PortalHostNode=SA&NoCrumbs=yes"
    
    driver = setup_driver(headless=False)  # Set to True to hide browser
    wait = WebDriverWait(driver, 10)
    
    try:
        print("Loading Olympic College course catalog...")
        driver.get(url)
        
        # Wait for page to load
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(3)  # Additional wait for dynamic content
        
        print("Taking screenshot...")
        driver.save_screenshot("olympic_catalog_page.png")
        
        # Look for iframe (common in CTCLink)
        try:
            iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe")))
            print(f"Found iframe: {iframe.get_attribute('name') or iframe.get_attribute('id')}")
            driver.switch_to.frame(iframe)
            time.sleep(2)
            print("Switched to iframe")
            driver.save_screenshot("inside_iframe.png")
        except:
            print("No iframe found, working with main page")
        
        # Now let's explore what's on the page to find course prefixes
        print("\n=== Exploring page content ===")
        
        # Look for common elements that might contain course prefixes
        selectors_to_try = [
            "select option",  # Dropdown options
            "a[href*='subject']",  # Links with subject in URL
            "a[href*='course']",  # Links with course in URL
            "td",  # Table cells
            "li",  # List items
            "div",  # Divs
            "span"  # Spans
        ]
        
        prefixes = set()  # Use set to avoid duplicates
        
        for selector in selectors_to_try:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"Found {len(elements)} elements with selector '{selector}'")
                
                for element in elements[:20]:  # Check first 20 elements
                    text = element.text.strip()
                    if text and len(text) >= 2 and len(text) <= 6:  # Course prefixes are typically 2-6 chars
                        # Check if it looks like a course prefix (letters, possibly with numbers)
                        if text.replace(' ', '').replace('-', '').isalnum() and any(c.isalpha() for c in text):
                            # Common course prefix patterns: MATH, CS, ENGL, BIO, etc.
                            if text.isupper() or (text.isalpha() and len(text) <= 5):
                                prefixes.add(text)
                                print(f"  Found potential prefix: '{text}'")
                
            except Exception as e:
                print(f"Error with selector '{selector}': {e}")
                continue
        
        # Also look at all text on the page and extract potential course codes
        print("\n=== Looking for course code patterns in page text ===")
        page_text = driver.page_source
        
        # Look for patterns like "MATH 101", "ENGL&101", etc.
        import re
        course_pattern = r'\b([A-Z]{2,5})[\s&]?\d{3}\b'
        matches = re.findall(course_pattern, page_text)
        
        for match in matches[:20]:  # First 20 matches
            prefixes.add(match)
            print(f"  Found course prefix from pattern: '{match}'")
        
        # Print all found prefixes
        print(f"\n=== FOUND {len(prefixes)} COURSE PREFIXES ===")
        sorted_prefixes = sorted(list(prefixes))
        for i, prefix in enumerate(sorted_prefixes, 1):
            print(f"{i:2d}. {prefix}")
        
        return sorted_prefixes
        
    except Exception as e:
        print(f"Error: {e}")
        return []
        
    finally:
        print("\nClosing browser...")
        driver.quit()

if __name__ == "__main__":
    print("Olympic College Course Prefix Extractor")
    print("=" * 40)
    
    prefixes = extract_course_prefixes()
    
    if prefixes:
        print(f"\nSuccess! Found {len(prefixes)} course prefixes.")
        
        # Save to file
        with open("olympic_course_prefixes.txt", "w") as f:
            for prefix in prefixes:
                f.write(f"{prefix}\n")
        print("Prefixes saved to: olympic_course_prefixes.txt")
        
    else:
        print("No course prefixes found. Check the screenshots to see what the page looks like.")
        
    print("\nDone!")