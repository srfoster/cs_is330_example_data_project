"""
Debug version of the course catalog scraper
This version provides detailed logging and exploration of iframe content
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import logging
from datetime import datetime

class DebugCourseScraperCTCLink:
    def __init__(self, headless=False, wait_timeout=15):
        self.wait_timeout = wait_timeout
        self.setup_logging()
        self.setup_driver(headless)
        
    def setup_logging(self):
        """Set up detailed logging"""
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('debug_scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_driver(self, headless):
        """Initialize Chrome WebDriver with debug settings"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, self.wait_timeout)
        self.logger.info("Chrome driver initialized for debugging")
        
    def take_screenshot(self, filename):
        """Take screenshot with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        full_filename = f"{timestamp}_{filename}"
        self.driver.save_screenshot(full_filename)
        self.logger.info(f"Screenshot saved: {full_filename}")
        return full_filename
        
    def debug_page_content(self, context_name="main"):
        """Debug current page content and structure"""
        self.logger.info(f"=== DEBUGGING {context_name.upper()} PAGE ===")
        
        # Basic page info
        self.logger.info(f"Current URL: {self.driver.current_url}")
        self.logger.info(f"Page Title: {self.driver.title}")
        
        # Find all links
        try:
            links = self.driver.find_elements(By.TAG_NAME, "a")
            self.logger.info(f"Found {len(links)} links:")
            for i, link in enumerate(links[:20]):  # Limit to first 20
                href = link.get_attribute('href') or 'No href'
                text = link.text.strip() or 'No text'
                title = link.get_attribute('title') or 'No title'
                self.logger.info(f"  Link {i+1}: '{text}' -> {href} (title: {title})")
                
                # Check for Olympic College specifically
                if 'olympic' in text.lower() or 'olympic' in href.lower() or 'olympic' in title.lower():
                    self.logger.info(f"  *** OLYMPIC COLLEGE LINK FOUND: {text} -> {href}")
                    
        except Exception as e:
            self.logger.error(f"Error finding links: {e}")
            
        # Find all forms and inputs
        try:
            forms = self.driver.find_elements(By.TAG_NAME, "form")
            self.logger.info(f"Found {len(forms)} forms:")
            for i, form in enumerate(forms):
                action = form.get_attribute('action') or 'No action'
                method = form.get_attribute('method') or 'No method'
                self.logger.info(f"  Form {i+1}: action='{action}' method='{method}'")
                
            # Find input elements
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            selects = self.driver.find_elements(By.TAG_NAME, "select")
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            
            self.logger.info(f"Found {len(inputs)} inputs, {len(selects)} selects, {len(buttons)} buttons")
            
            # Log select options
            for i, select in enumerate(selects[:5]):  # First 5 selects
                try:
                    select_obj = Select(select)
                    options = [opt.text for opt in select_obj.options[:10]]  # First 10 options
                    name = select.get_attribute('name') or f'select_{i}'
                    self.logger.info(f"  Select '{name}': {options}")
                except Exception as e:
                    self.logger.debug(f"Error reading select {i}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error finding forms: {e}")
            
        # Look for navigation elements
        try:
            nav_elements = self.driver.find_elements(By.CSS_SELECTOR, "nav, .nav, .navigation, .menu, ul.menu")
            self.logger.info(f"Found {len(nav_elements)} navigation elements")
            
            for i, nav in enumerate(nav_elements):
                nav_links = nav.find_elements(By.TAG_NAME, "a")
                self.logger.info(f"  Nav {i+1}: {len(nav_links)} links")
                for j, link in enumerate(nav_links[:10]):
                    text = link.text.strip()
                    href = link.get_attribute('href')
                    if text:
                        self.logger.info(f"    Nav link {j+1}: '{text}' -> {href}")
                        
        except Exception as e:
            self.logger.error(f"Error finding navigation: {e}")
        
        self.logger.info(f"=== END {context_name.upper()} DEBUG ===")
        
    def explore_site(self, base_url):
        """Comprehensive site exploration"""
        try:
            self.logger.info("Starting comprehensive site exploration...")
            
            # Navigate to main page
            self.logger.info(f"Navigating to: {base_url}")
            self.driver.get(base_url)
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(3)
            
            self.take_screenshot("01_initial_page.png")
            self.debug_page_content("main")
            
            # Look for iframe
            try:
                iframe = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe")))
                self.logger.info("Found iframe, switching context...")
                
                iframe_src = iframe.get_attribute('src')
                self.logger.info(f"Iframe src: {iframe_src}")
                
                self.driver.switch_to.frame(iframe)
                time.sleep(3)
                
                self.take_screenshot("02_inside_iframe.png")
                self.debug_page_content("iframe")
                
                # Try to find college selection or Olympic College specific content
                self.look_for_college_options()
                
                # Look for course search interface
                self.explore_course_search()
                
            except TimeoutException:
                self.logger.info("No iframe found")
                self.explore_course_search()
                
        except Exception as e:
            self.logger.error(f"Error in site exploration: {e}")
            
    def look_for_college_options(self):
        """Look for college selection options"""
        self.logger.info("=== LOOKING FOR COLLEGE OPTIONS ===")
        
        # Look for dropdowns that might contain college options
        try:
            selects = self.driver.find_elements(By.TAG_NAME, "select")
            for i, select in enumerate(selects):
                try:
                    select_obj = Select(select)
                    name = select.get_attribute('name') or f'select_{i}'
                    id_attr = select.get_attribute('id') or f'no_id_{i}'
                    
                    self.logger.info(f"Select element: name='{name}' id='{id_attr}'")
                    
                    for j, option in enumerate(select_obj.options):
                        option_text = option.text
                        option_value = option.get_attribute('value')
                        
                        if 'olympic' in option_text.lower() or 'olympic' in option_value.lower():
                            self.logger.info(f"*** OLYMPIC COLLEGE OPTION FOUND: '{option_text}' (value: '{option_value}')")
                        
                        if j < 10:  # Log first 10 options
                            self.logger.info(f"  Option {j+1}: '{option_text}' (value: '{option_value}')")
                            
                except Exception as e:
                    self.logger.debug(f"Error reading select {i}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error looking for college options: {e}")
            
    def explore_course_search(self):
        """Explore course search interface"""
        self.logger.info("=== EXPLORING COURSE SEARCH INTERFACE ===")
        
        # Look for common course search elements
        search_indicators = [
            ("Subject dropdowns", "select[name*='subject'], select[id*='subject']"),
            ("Term dropdowns", "select[name*='term'], select[id*='term']"),
            ("Search buttons", "input[type='submit'], button[type='submit'], input[value*='Search']"),
            ("Course inputs", "input[name*='course'], input[id*='course']"),
            ("Department selects", "select[name*='dept'], select[id*='dept']")
        ]
        
        for description, selector in search_indicators:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                self.logger.info(f"{description}: Found {len(elements)} elements")
                
                for i, elem in enumerate(elements[:3]):  # First 3 elements
                    name = elem.get_attribute('name') or 'no_name'
                    id_attr = elem.get_attribute('id') or 'no_id'
                    tag = elem.tag_name
                    self.logger.info(f"  {tag} {i+1}: name='{name}' id='{id_attr}'")
                    
                    if tag == 'select':
                        try:
                            select_obj = Select(elem)
                            option_count = len(select_obj.options)
                            self.logger.info(f"    Has {option_count} options")
                            
                            if option_count > 0 and option_count < 50:  # Reasonable number to log
                                for opt in select_obj.options[:10]:
                                    self.logger.info(f"      '{opt.text}' (value: '{opt.get_attribute('value')}')")
                        except Exception as e:
                            self.logger.debug(f"Error reading select options: {e}")
                            
            except Exception as e:
                self.logger.debug(f"Error finding {description}: {e}")
                
        # Look for any text that mentions courses or subjects
        try:
            body_text = self.driver.find_element(By.TAG_NAME, "body").text
            if 'subject' in body_text.lower() or 'course' in body_text.lower():
                self.logger.info("Page contains course/subject related text")
            else:
                self.logger.warning("Page does not seem to contain course search interface")
                
        except Exception as e:
            self.logger.error(f"Error reading page text: {e}")
            
    def close(self):
        """Clean up"""
        if hasattr(self, 'driver'):
            self.driver.quit()
            self.logger.info("Debug driver closed")

# Usage
if __name__ == "__main__":
    print("=== DEBUG COURSE CATALOG SCRAPER ===")
    print("This will provide detailed analysis of the site structure")
    print()
    
    debug_scraper = DebugCourseScraperCTCLink(headless=False)
    
    catalog_url = "https://csprd.ctclink.us/psp/csprd/EMPLOYEE/SA/s/WEBLIB_HCX_CM.H_COURSE_CATALOG.FieldFormula.IScript_Main"
    
    try:
        debug_scraper.explore_site(catalog_url)
        print("\nDebug exploration complete. Check debug_scraper.log for detailed findings.")
        
    except KeyboardInterrupt:
        print("\nDebug interrupted by user")
    except Exception as e:
        print(f"Debug failed: {e}")
    finally:
        debug_scraper.close()