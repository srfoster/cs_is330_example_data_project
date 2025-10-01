"""
Focused Course Prefix Extractor for Olympic College
This script will open the page and look for course prefixes in common locations
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re
import json
from datetime import datetime

def extract_course_prefixes():
    chrome_options = Options()
    # chrome_options.add_argument('--headless')  # Comment out to see what's happening
    
    # Suppress Chrome's verbose logging (including TensorFlow messages)
    chrome_options.add_argument('--log-level=3')  # Only show fatal errors
    chrome_options.add_argument('--disable-logging')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--no-sandbox')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    url = "https://csprd.ctclink.us/psp/csprd/EMPLOYEE/SA/s/WEBLIB_HCX_CM.H_COURSE_CATALOG.FieldFormula.IScript_Main?institution=WA030&PortalActualURL=https%3a%2f%2fcsprd.ctclink.us%2fpsc%2fcsprd%2fEMPLOYEE%2fSA%2fs%2fWEBLIB_HCX_CM.H_COURSE_CATALOG.FieldFormula.IScript_Main&PortalContentURL=https%3a%2f%2fcsprd.ctclink.us%2fpsc%2fcsprd%2fEMPLOYEE%2fSA%2fs%2fWEBLIB_HCX_CM.H_COURSE_CATALOG.FieldFormula.IScript_Main&PortalContentProvider=SA&PortalCRefLabel=Course%20Catalog&PortalRegistryName=EMPLOYEE&PortalServletURI=https%3a%2f%2fcsprd.ctclink.us%2fpsp%2fcsprd%2f&PortalURI=https%3a%2f%2fcsprd.ctclink.us%2fpsc%2fcsprd%2f&PortalHostNode=SA&NoCrumbs=yes"
    
    prefixes = set()
    
    try:
        print("🌐 Loading Olympic College course catalog...")
        driver.get(url)
        time.sleep(5)
        
        # Switch to iframe if present
        try:
            iframe = driver.find_element(By.CSS_SELECTOR, "iframe")
            driver.switch_to.frame(iframe)
            print("✅ Switched to iframe")
            time.sleep(3)
        except:
            print("ℹ️  No iframe found, working with main page")
        
        print("\n🔍 Searching for course prefixes...")
        
        # Strategy 1: Look for clickable links that might be subject/department codes
        links = driver.find_elements(By.TAG_NAME, "a")
        print(f"   Found {len(links)} links to analyze")
        
        for link in links:
            try:
                text = link.text.strip()
                href = link.get_attribute('href') or ''
                
                # Look for short text that could be course prefixes
                if text and 2 <= len(text) <= 6:
                    # Check if it looks like a course prefix
                    if text.isupper() and text.replace('&', '').isalpha():
                        prefixes.add(text)
                        print(f"   📚 Found prefix: {text}")
                    
                    # Also check for patterns in href like subject=MATH
                    subject_match = re.search(r'subject=([A-Z&]+)', href)
                    if subject_match:
                        prefix = subject_match.group(1)
                        prefixes.add(prefix)
                        print(f"   📚 Found prefix from URL: {prefix}")
                        
            except:
                continue
        
        # Strategy 2: Look for select dropdowns with options
        selects = driver.find_elements(By.TAG_NAME, "select")
        print(f"   Found {len(selects)} dropdown menus")
        
        for select in selects:
            try:
                options = select.find_elements(By.TAG_NAME, "option")
                for option in options:
                    text = option.text.strip()
                    value = option.get_attribute('value') or ''
                    
                    # Look for course prefixes in option text or value
                    for item in [text, value]:
                        if item and 2 <= len(item) <= 6 and item.isupper() and item.replace('&', '').isalpha():
                            prefixes.add(item)
                            print(f"   📚 Found prefix in dropdown: {item}")
            except:
                continue
        
        # Strategy 3: Look in page source for common patterns
        page_source = driver.page_source
        
        # Look for subject codes in URLs
        url_patterns = re.findall(r'subject=([A-Z&]{2,6})', page_source)
        for pattern in url_patterns:
            prefixes.add(pattern)
            print(f"   📚 Found prefix in page source: {pattern}")
        
        # Strategy 4: Look for text patterns like "MATH - Mathematics"
        text_patterns = re.findall(r'\b([A-Z&]{2,6})\s*-\s*[A-Z]', page_source)
        for pattern in text_patterns:
            if pattern.replace('&', '').isalpha():
                prefixes.add(pattern)
                print(f"   📚 Found prefix with description: {pattern}")
        
        return sorted(list(prefixes))
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []
        
    finally:
        print("\n🔒 Closing browser...")
        driver.quit()

if __name__ == "__main__":
    print("🎓 Olympic College Course Prefix Extractor")
    print("=" * 50)
    
    prefixes = extract_course_prefixes()
    
    if prefixes:
        print(f"\n🎉 SUCCESS! Found {len(prefixes)} course prefixes:")
        print("-" * 30)
        
        for i, prefix in enumerate(prefixes, 1):
            print(f"{i:2d}. {prefix}")
        
        # Save to text file
        txt_filename = "olympic_course_prefixes_final.txt"
        with open(txt_filename, "w") as f:
            for prefix in prefixes:
                f.write(f"{prefix}\n")
        
        # Save to JSON file with metadata
        json_filename = "olympic_course_prefixes_final.json"
        json_data = {
            "extracted_at": datetime.now().isoformat(),
            "source_url": "https://csprd.ctclink.us/psp/csprd/EMPLOYEE/SA/s/WEBLIB_HCX_CM.H_COURSE_CATALOG.FieldFormula.IScript_Main",
            "institution": "Olympic College (WA030)",
            "total_prefixes": len(prefixes),
            "course_prefixes": prefixes,
            "extraction_method": "Multi-strategy Selenium scraping"
        }
        
        with open(json_filename, "w", encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Prefixes saved to:")
        print(f"   📄 Text format: {txt_filename}")
        print(f"   📋 JSON format: {json_filename}")
        
    else:
        print("\n😞 No course prefixes found.")
        print("The page might need manual inspection to understand its structure.")
    
    print("\n✨ Done!")