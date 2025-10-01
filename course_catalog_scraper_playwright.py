"""
Alternative scraper using Playwright
Playwright can be more reliable for some dynamic sites
"""

from playwright.sync_api import sync_playwright
import json
import csv
from datetime import datetime
import logging
import time

class CourseScraperPlaywright:
    def __init__(self, headless=True):
        self.headless = headless
        self.setup_logging()
        self.courses_data = []
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def scrape_catalog(self, url):
        """Main scraping method using Playwright"""
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page()
            
            try:
                self.logger.info(f"Navigating to: {url}")
                page.goto(url, wait_until="networkidle")
                
                # Wait for page to fully load
                page.wait_for_timeout(3000)
                
                # Try to find and enter main iframe if present
                try:
                    iframe = page.frame_locator("iframe[name='main_iframe']")
                    if iframe:
                        self.logger.info("Found main iframe, working within it")
                        self._scrape_within_frame(iframe)
                except:
                    self.logger.info("No iframe found or accessible, scraping main page")
                    self._scrape_main_page(page)
                    
                # Take a screenshot for debugging
                page.screenshot(path="course_catalog_screenshot.png")
                self.logger.info("Screenshot saved as course_catalog_screenshot.png")
                
            except Exception as e:
                self.logger.error(f"Error during scraping: {e}")
            finally:
                browser.close()
                
        return len(self.courses_data) > 0
        
    def _scrape_within_frame(self, iframe):
        """Scrape content within iframe"""
        try:
            # Look for course search elements
            subjects = iframe.locator("select[name*='subject'], select[id*='subject']")
            if subjects.count() > 0:
                self.logger.info("Found subject dropdown in iframe")
                # Get all options
                options = subjects.locator("option").all()
                for option in options[:5]:  # Limit for testing
                    value = option.get_attribute("value")
                    text = option.text_content()
                    if value and value.strip():
                        self.logger.info(f"Processing subject: {text}")
                        self._search_subject_in_frame(iframe, value)
            else:
                # Extract any visible course data
                self._extract_course_data_from_frame(iframe)
                
        except Exception as e:
            self.logger.error(f"Error scraping within frame: {e}")
            
    def _search_subject_in_frame(self, iframe, subject_code):
        """Search for courses in a specific subject within iframe"""
        try:
            # Select subject
            iframe.locator("select[name*='subject']").select_option(subject_code)
            
            # Click search button
            search_btn = iframe.locator("input[type='submit'], button[type='submit']").first
            search_btn.click()
            
            # Wait for results
            iframe.page.wait_for_timeout(3000)
            
            # Extract course data
            self._extract_course_data_from_frame(iframe)
            
        except Exception as e:
            self.logger.error(f"Error searching subject {subject_code}: {e}")
            
    def _extract_course_data_from_frame(self, iframe):
        """Extract course data from iframe content"""
        try:
            # Look for course listings with various selectors
            selectors = [
                "tr:has-text('course')",
                "div:has-text('course')",
                "table tr",
                "[class*='course']",
                "tr"
            ]
            
            for selector in selectors:
                elements = iframe.locator(selector)
                count = elements.count()
                if count > 0:
                    self.logger.info(f"Found {count} elements with selector: {selector}")
                    for i in range(min(count, 20)):  # Limit to prevent timeout
                        try:
                            element = elements.nth(i)
                            text = element.text_content()
                            if text and len(text.strip()) > 10:
                                course_data = {
                                    'raw_text': text.strip(),
                                    'extracted_at': datetime.now().isoformat(),
                                    'selector_used': selector
                                }
                                self.courses_data.append(course_data)
                        except:
                            continue
                    break
                    
        except Exception as e:
            self.logger.error(f"Error extracting course data: {e}")
            
    def _scrape_main_page(self, page):
        """Scrape content from main page (no iframe)"""
        try:
            # Get page content
            content = page.content()
            
            # Look for links to course sections
            links = page.locator("a").all()
            for link in links:
                href = link.get_attribute("href")
                text = link.text_content()
                if text and ("course" in text.lower() or "class" in text.lower()):
                    self.logger.info(f"Found relevant link: {text} -> {href}")
                    
            # Try to click on "Browse Classes" or similar
            try:
                browse_link = page.locator("text=Browse Classes").first
                browse_link.click()
                page.wait_for_timeout(3000)
                self._extract_any_visible_data(page)
            except:
                self.logger.info("Could not find or click Browse Classes link")
                
        except Exception as e:
            self.logger.error(f"Error scraping main page: {e}")
            
    def _extract_any_visible_data(self, page):
        """Extract any visible course-related data"""
        try:
            # Get all text content
            all_text = page.locator("body").text_content()
            
            # Save raw page content for analysis
            raw_data = {
                'page_content': all_text,
                'extracted_at': datetime.now().isoformat(),
                'page_title': page.title(),
                'url': page.url
            }
            self.courses_data.append(raw_data)
            
        except Exception as e:
            self.logger.error(f"Error extracting visible data: {e}")
            
    def save_data(self, format='json'):
        """Save scraped data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == 'json':
            filename = f"course_catalog_playwright_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.courses_data, f, indent=2, ensure_ascii=False)
        elif format == 'csv':
            filename = f"course_catalog_playwright_{timestamp}.csv"
            # Handle mixed data types for CSV
            if self.courses_data:
                # Flatten the data structure for CSV
                flattened_data = []
                for item in self.courses_data:
                    if isinstance(item, dict):
                        flattened_data.append(item)
                
                if flattened_data:
                    fieldnames = set()
                    for item in flattened_data:
                        fieldnames.update(item.keys())
                    
                    with open(filename, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=list(fieldnames))
                        writer.writeheader()
                        writer.writerows(flattened_data)
                        
        self.logger.info(f"Data saved to: {filename}")
        return filename

# Example usage
if __name__ == "__main__":
    scraper = CourseScraperPlaywright(headless=False)
    
    catalog_url = "https://csprd.ctclink.us/psp/csprd/EMPLOYEE/SA/s/WEBLIB_HCX_CM.H_COURSE_CATALOG.FieldFormula.IScript_Main"
    
    try:
        success = scraper.scrape_catalog(catalog_url)
        if success:
            scraper.save_data('json')
            scraper.save_data('csv')
            print(f"Successfully scraped {len(scraper.courses_data)} items")
        else:
            print("No data was scraped")
            
    except Exception as e:
        print(f"Scraping failed: {e}")