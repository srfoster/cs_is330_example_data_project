"""
Course Catalog Scraper for CTCLink System
Automates scraping of dynamic course catalog interfaces
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import json
import csv
from datetime import datetime
import logging

class CourseScraperCTCLink:
    def __init__(self, headless=True, wait_timeout=10):
        """
        Initialize the scraper with Chrome driver
        
        Args:
            headless (bool): Run browser in headless mode
            wait_timeout (int): Timeout for waiting for elements
        """
        self.wait_timeout = wait_timeout
        self.setup_logging()
        self.setup_driver(headless)
        self.courses_data = []
        
    def setup_logging(self):
        """Set up logging for debugging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('course_scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_driver(self, headless):
        """Initialize Chrome WebDriver"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, self.wait_timeout)
            self.logger.info("Chrome driver initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Chrome driver: {e}")
            raise
            
    def take_screenshot(self, filename=None):
        """Take a screenshot for debugging purposes"""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"scraper_screenshot_{timestamp}.png"
                
            self.driver.save_screenshot(filename)
            self.logger.info(f"Screenshot saved: {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {e}")
            return None
            
    def save_page_source(self, filename=None):
        """Save current page source for debugging"""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"page_source_{timestamp}.html"
                
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            self.logger.info(f"Page source saved: {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Failed to save page source: {e}")
            return None

class CourseScraperCTCLink:
    def __init__(self, headless=True, wait_timeout=10):
        """
        Initialize the scraper with Chrome driver
        
        Args:
            headless (bool): Run browser in headless mode
            wait_timeout (int): Timeout for waiting for elements
        """
        self.wait_timeout = wait_timeout
        self.setup_logging()
        self.setup_driver(headless)
        self.courses_data = []
        
    def setup_logging(self):
        """Set up logging for debugging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('course_scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_driver(self, headless):
        """Initialize Chrome WebDriver"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, self.wait_timeout)
            self.logger.info("Chrome driver initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Chrome driver: {e}")
            raise
            
    def navigate_to_catalog(self, base_url):
        """Navigate to the course catalog main page"""
        try:
            self.logger.info(f"Navigating to: {base_url}")
            self.driver.get(base_url)
            
            # Wait for page to load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(2)  # Additional wait for dynamic content
            
            # Take screenshot after page loads
            self.take_screenshot("01_page_loaded.png")
            
            # Check if we're already on Olympic College page (direct URL)
            current_url = self.driver.current_url.lower()
            if 'institution=wa030' in current_url or 'olympic' in current_url:
                self.logger.info("Already on Olympic College page (direct URL)")
                self.take_screenshot("02_olympic_college_page.png")
            else:
                # Try to find Olympic College link if we're on the general page
                if self.click_olympic_college_link():
                    self.logger.info("Successfully clicked Olympic College link")
                    time.sleep(3)  # Wait for navigation
                    self.take_screenshot("02_olympic_college_page.png")
                else:
                    self.logger.info("Olympic College link not found, continuing with current page")
            
            self.logger.info("Successfully loaded catalog page")
            return True
            
        except TimeoutException:
            self.logger.error("Timeout waiting for page to load")
            return False
        except Exception as e:
            self.logger.error(f"Error navigating to catalog: {e}")
            return False
            
    def click_olympic_college_link(self):
        """Find and click on Olympic College link in navigation"""
        try:
            self.logger.info("Searching for Olympic College link...")
            
            # Wait a bit more for page to fully load
            time.sleep(3)
            
            # First, let's see what links are available for debugging
            all_links = self.driver.find_elements(By.TAG_NAME, "a")
            self.logger.info(f"Found {len(all_links)} total links on page")
            
            # Log first few links to help debug
            for i, link in enumerate(all_links[:10]):
                link_text = link.text.strip()
                link_href = link.get_attribute('href') or ''
                if link_text:  # Only log links with text
                    self.logger.info(f"Link {i+1}: '{link_text}' -> {link_href}")
            
            # Enhanced search patterns for Olympic College
            olympic_patterns = [
                'olympic college',
                'olympic',
                'oc ',  # Common abbreviation
                'olympic.edu'
            ]
            
            # Search through all links for Olympic College
            for link in all_links:
                try:
                    link_text = (link.text or '').strip().lower()
                    link_href = (link.get_attribute('href') or '').lower()
                    link_title = (link.get_attribute('title') or '').lower()
                    
                    # Check if any Olympic pattern matches
                    for pattern in olympic_patterns:
                        if (pattern in link_text or 
                            pattern in link_href or 
                            pattern in link_title):
                            
                            self.logger.info(f"FOUND Olympic College link!")
                            self.logger.info(f"  Text: '{link.text}'")
                            self.logger.info(f"  Href: '{link.get_attribute('href')}'")
                            self.logger.info(f"  Title: '{link.get_attribute('title')}'")
                            self.logger.info(f"  Matched pattern: '{pattern}'")
                            
                            # Make sure link is visible
                            if link.is_displayed() and link.is_enabled():
                                # Scroll to element
                                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link)
                                time.sleep(1)
                                
                                # Highlight the element (for debugging)
                                self.driver.execute_script("arguments[0].style.border='3px solid red';", link)
                                time.sleep(1)
                                
                                # Try to click
                                try:
                                    link.click()
                                    self.logger.info("Successfully clicked Olympic College link!")
                                    return True
                                except Exception as click_error:
                                    self.logger.warning(f"Click failed, trying JavaScript click: {click_error}")
                                    try:
                                        self.driver.execute_script("arguments[0].click();", link)
                                        self.logger.info("Successfully clicked Olympic College link with JavaScript!")
                                        return True
                                    except Exception as js_error:
                                        self.logger.error(f"JavaScript click also failed: {js_error}")
                                        
                            else:
                                self.logger.warning(f"Olympic link found but not clickable (visible: {link.is_displayed()}, enabled: {link.is_enabled()})")
                                
                except Exception as e:
                    self.logger.debug(f"Error checking link: {e}")
                    continue
            
            # If we get here, no Olympic College link was found
            self.logger.warning("No Olympic College link found on this page")
            self.logger.info("Available link texts (first 20):")
            for i, link in enumerate(all_links[:20]):
                link_text = (link.text or '').strip()
                if link_text:
                    self.logger.info(f"  {i+1}. '{link_text}'")
            
            # Save page source for debugging
            self.save_page_source("debug_no_olympic_link.html")
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error searching for Olympic College link: {e}")
            return False
            
    def find_course_search_interface(self):
        """Locate and interact with course search forms"""
        try:
            self.logger.info("Looking for course search interface...")
            
            # Try to find main iframe first (common in CTCLink)
            try:
                iframe = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "iframe"))
                )
                self.logger.info(f"Found iframe: {iframe.get_attribute('name') or iframe.get_attribute('id')}")
                self.driver.switch_to.frame(iframe)
                self.logger.info("Switched to main iframe")
                
                # Take screenshot after switching to iframe
                self.take_screenshot("03_inside_iframe.png")
                
                # Wait for iframe content to load
                time.sleep(3)
                
            except TimeoutException:
                self.logger.info("No iframe found, continuing with main page")
                self.take_screenshot("03_main_page_no_iframe.png")
            
            # Now let's explore what's actually in the iframe/page
            self.logger.info("Exploring page content...")
            
            # Look for any forms
            forms = self.driver.find_elements(By.TAG_NAME, "form")
            self.logger.info(f"Found {len(forms)} forms")
            
            # Look for select elements (dropdowns)
            selects = self.driver.find_elements(By.TAG_NAME, "select")
            self.logger.info(f"Found {len(selects)} select elements")
            for i, select in enumerate(selects[:5]):  # Log first 5
                name = select.get_attribute('name') or select.get_attribute('id') or f'select_{i}'
                self.logger.info(f"  Select: {name}")
                
            # Look for input elements
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            self.logger.info(f"Found {len(inputs)} input elements")
            
            # Look for buttons
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            self.logger.info(f"Found {len(buttons)} buttons")
            
            # Look for links that might be navigation
            links = self.driver.find_elements(By.TAG_NAME, "a")
            self.logger.info(f"Found {len(links)} links in iframe")
            for i, link in enumerate(links[:10]):  # Log first 10 links
                link_text = (link.text or '').strip()
                if link_text:
                    self.logger.info(f"  Link: '{link_text}'")
            
            # Enhanced search for course-related elements
            course_selectors = [
                "select[name*='subject']", "select[id*='subject']",
                "select[name*='term']", "select[id*='term']", 
                "select[name*='course']", "select[id*='course']",
                "select[name*='dept']", "select[id*='dept']",
                "input[type='submit']", "button[type='submit']",
                "form", "table", "div[class*='search']",
                "a[href*='browse']", "a[href*='search']", "a[href*='class']"
            ]
            
            found_elements = []
            for selector in course_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        self.logger.info(f"Found {len(elements)} elements with selector: {selector}")
                        found_elements.extend(elements)
                except Exception as e:
                    continue
            
            # If we found any course-related elements, consider it a success
            if found_elements:
                self.logger.info(f"Found {len(found_elements)} total course-related elements")
                return True
            else:
                # Let's get the page source to see what's actually there
                page_source = self.driver.page_source
                self.logger.info(f"Page source length: {len(page_source)} characters")
                
                # Look for key terms in the page source
                key_terms = ['course', 'class', 'search', 'browse', 'catalog', 'subject', 'department']
                for term in key_terms:
                    count = page_source.lower().count(term)
                    if count > 0:
                        self.logger.info(f"Found '{term}' {count} times in page source")
                
                self.logger.warning("No obvious course search interface found")
                return False
                
        except Exception as e:
            self.logger.error(f"Error finding search interface: {e}")
            return False
            
    def get_available_subjects(self):
        """Extract available subjects/departments"""
        subjects = []
        try:
            # Look for subject dropdown
            subject_selectors = [
                "select[name*='subject']",
                "select[id*='subject']",
                "select[name*='dept']",
                "select[id*='dept']",
            ]
            
            for selector in subject_selectors:
                try:
                    subject_dropdown = self.driver.find_element(By.CSS_SELECTOR, selector)
                    select = Select(subject_dropdown)
                    
                    for option in select.options:
                        if option.value and option.value != "":
                            subjects.append({
                                'code': option.value,
                                'name': option.text
                            })
                    
                    self.logger.info(f"Found {len(subjects)} subjects")
                    return subjects
                    
                except NoSuchElementException:
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error getting subjects: {e}")
            
        return subjects
        
    def search_courses_by_subject(self, subject_code):
        """Search for courses in a specific subject"""
        try:
            # Select subject
            subject_dropdown = self.driver.find_element(By.CSS_SELECTOR, "select[name*='subject']")
            select = Select(subject_dropdown)
            select.select_by_value(subject_code)
            
            # Submit search
            search_button = self.driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")
            search_button.click()
            
            # Wait for results
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(3)  # Wait for dynamic loading
            
            # Take screenshot after search results load
            self.take_screenshot(f"04_search_results_{subject_code}.png")
            
            return self.extract_course_data()
            
        except Exception as e:
            self.logger.error(f"Error searching courses for {subject_code}: {e}")
            return []
            
    def extract_course_data(self):
        """Extract course data from search results"""
        courses = []
        try:
            # Common patterns for course listings
            course_selectors = [
                "tr[class*='course']",
                "div[class*='course']",
                "table tr",
                ".course-row",
                "[id*='course']"
            ]
            
            for selector in course_selectors:
                try:
                    course_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if course_elements:
                        self.logger.info(f"Found {len(course_elements)} course elements with selector: {selector}")
                        
                        for element in course_elements:
                            course_data = self.parse_course_element(element)
                            if course_data:
                                courses.append(course_data)
                        break
                        
                except Exception as e:
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error extracting course data: {e}")
            
        return courses
        
    def parse_course_element(self, element):
        """Parse individual course element for data"""
        try:
            # Extract text content and look for patterns
            text = element.text.strip()
            if not text or len(text) < 10:  # Skip empty or very short elements
                return None
                
            # Basic course data structure
            course_data = {
                'raw_text': text,
                'extracted_at': datetime.now().isoformat(),
                'course_code': '',
                'course_title': '',
                'credits': '',
                'instructor': '',
                'schedule': '',
                'location': ''
            }
            
            # Try to extract course code (common pattern: ABC 123)
            import re
            code_match = re.search(r'\b[A-Z]{2,4}\s+\d{3}\b', text)
            if code_match:
                course_data['course_code'] = code_match.group()
                
            return course_data
            
        except Exception as e:
            self.logger.error(f"Error parsing course element: {e}")
            return None
            
    def scrape_full_catalog(self, base_url):
        """Main method to scrape the entire catalog"""
        try:
            # Navigate to catalog
            if not self.navigate_to_catalog(base_url):
                return False
                
            # Find search interface
            if not self.find_course_search_interface():
                self.logger.error("Could not find course search interface")
                return False
                
            # Get available subjects
            subjects = self.get_available_subjects()
            if not subjects:
                self.logger.warning("No subjects found, attempting to scrape current page")
                courses = self.extract_course_data()
                self.courses_data.extend(courses)
            else:
                # Scrape each subject
                for subject in subjects[:5]:  # Limit to first 5 for testing
                    self.logger.info(f"Scraping subject: {subject['code']} - {subject['name']}")
                    courses = self.search_courses_by_subject(subject['code'])
                    self.courses_data.extend(courses)
                    time.sleep(2)  # Respectful delay
                    
            self.logger.info(f"Total courses scraped: {len(self.courses_data)}")
            
            # Take final screenshot
            self.take_screenshot("05_scraping_complete.png")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error in full catalog scrape: {e}")
            return False
            
    def save_data(self, format='json'):
        """Save scraped data to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == 'json':
            filename = f"course_catalog_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.courses_data, f, indent=2, ensure_ascii=False)
                
        elif format == 'csv':
            filename = f"course_catalog_{timestamp}.csv"
            if self.courses_data:
                fieldnames = self.courses_data[0].keys()
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(self.courses_data)
                    
        self.logger.info(f"Data saved to: {filename}")
        return filename
        
    def take_screenshot(self, filename=None):
        """Take a screenshot for debugging purposes"""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"scraper_screenshot_{timestamp}.png"
                
            self.driver.save_screenshot(filename)
            self.logger.info(f"Screenshot saved: {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {e}")
            return None
            
    def close(self):
        """Clean up resources"""
        if hasattr(self, 'driver'):
            self.driver.quit()
            self.logger.info("Driver closed")

# Example usage
if __name__ == "__main__":
    scraper = CourseScraperCTCLink(headless=False)  # Set to True for production
    
    # Direct URL to Olympic College course catalog
    catalog_url = "https://csprd.ctclink.us/psp/csprd/EMPLOYEE/SA/s/WEBLIB_HCX_CM.H_COURSE_CATALOG.FieldFormula.IScript_Main?institution=WA030&PortalActualURL=https%3a%2f%2fcsprd.ctclink.us%2fpsc%2fcsprd%2fEMPLOYEE%2fSA%2fs%2fWEBLIB_HCX_CM.H_COURSE_CATALOG.FieldFormula.IScript_Main&PortalContentURL=https%3a%2f%2fcsprd.ctclink.us%2fpsc%2fcsprd%2fEMPLOYEE%2fSA%2fs%2fWEBLIB_HCX_CM.H_COURSE_CATALOG.FieldFormula.IScript_Main&PortalContentProvider=SA&PortalCRefLabel=Course%20Catalog&PortalRegistryName=EMPLOYEE&PortalServletURI=https%3a%2f%2fcsprd.ctclink.us%2fpsp%2fcsprd%2f&PortalURI=https%3a%2f%2fcsprd.ctclink.us%2fpsc%2fcsprd%2f&PortalHostNode=SA&NoCrumbs=yes"
    
    try:
        success = scraper.scrape_full_catalog(catalog_url)
        if success:
            scraper.save_data('json')
            scraper.save_data('csv')
        else:
            print("Scraping failed. Check logs for details.")
            
    except KeyboardInterrupt:
        print("Scraping interrupted by user")
    finally:
        scraper.close()