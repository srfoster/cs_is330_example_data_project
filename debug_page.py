"""
Simple debug script to see what's actually on the Olympic College page
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

def debug_page():
    chrome_options = Options()
    # chrome_options.add_argument('--headless')  # Comment out to see browser
    driver = webdriver.Chrome(options=chrome_options)
    
    url = "https://csprd.ctclink.us/psp/csprd/EMPLOYEE/SA/s/WEBLIB_HCX_CM.H_COURSE_CATALOG.FieldFormula.IScript_Main?institution=WA030&PortalActualURL=https%3a%2f%2fcsprd.ctclink.us%2fpsc%2fcsprd%2fEMPLOYEE%2fSA%2fs%2fWEBLIB_HCX_CM.H_COURSE_CATALOG.FieldFormula.IScript_Main&PortalContentURL=https%3a%2f%2fcsprd.ctclink.us%2fpsc%2fcsprd%2fEMPLOYEE%2fSA%2fs%2fWEBLIB_HCX_CM.H_COURSE_CATALOG.FieldFormula.IScript_Main&PortalContentProvider=SA&PortalCRefLabel=Course%20Catalog&PortalRegistryName=EMPLOYEE&PortalServletURI=https%3a%2f%2fcsprd.ctclink.us%2fpsp%2fcsprd%2f&PortalURI=https%3a%2f%2fcsprd.ctclink.us%2fpsc%2fcsprd%2f&PortalHostNode=SA&NoCrumbs=yes"
    
    try:
        print("Loading page...")
        driver.get(url)
        time.sleep(5)
        
        print("Looking for iframe...")
        try:
            iframe = driver.find_element(By.CSS_SELECTOR, "iframe")
            driver.switch_to.frame(iframe)
            print("Switched to iframe")
            time.sleep(3)
        except:
            print("No iframe found")
        
        # Look for links that might contain course prefixes
        print("\nLooking for links...")
        links = driver.find_elements(By.TAG_NAME, "a")
        print(f"Found {len(links)} links")
        
        prefixes = set()
        for i, link in enumerate(links[:50]):  # Check first 50 links
            try:
                text = link.text.strip()
                href = link.get_attribute('href') or ''
                
                if text and len(text) <= 10:  # Short text that might be prefixes
                    print(f"Link {i+1}: '{text}' -> {href[:100]}...")
                    
                    # Look for course prefix patterns
                    if text.isupper() and len(text) >= 2 and len(text) <= 5 and text.isalpha():
                        prefixes.add(text)
                        
            except Exception as e:
                print(f"Error with link {i}: {e}")
        
        print(f"\nPotential course prefixes found: {sorted(prefixes)}")
        
        # Also look at page title and visible text
        print(f"\nPage title: {driver.title}")
        
        # Get all visible text
        try:
            body = driver.find_element(By.TAG_NAME, "body")
            visible_text = body.text[:1000]  # First 1000 characters
            print(f"\nFirst 1000 characters of visible text:")
            print(visible_text)
        except:
            print("Could not get body text")
            
        input("Press Enter to close browser...")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_page()