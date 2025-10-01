# Course Catalog Scraping Toolkit

This toolkit provides multiple approaches for scraping dynamic course catalog websites, specifically designed for CTCLink systems used by community and technical colleges.

## 🚀 Quick Start

1. **Run the analysis first:**
   ```bash
   python analyze_catalog.py
   ```

2. **Install dependencies:**
   ```bash
   # Windows
   setup_scraper.bat
   
   # Linux/Mac
   chmod +x setup_scraper.sh
   ./setup_scraper.sh
   ```

3. **Run the scraper:**
   ```bash
   # Option 1: Selenium (most compatible)
   python course_catalog_scraper.py
   
   # Option 2: Playwright (faster, modern)
   python course_catalog_scraper_playwright.py
   ```

## 📁 Files Overview

### Core Scrapers
- **`course_catalog_scraper.py`** - Main Selenium-based scraper
- **`course_catalog_scraper_playwright.py`** - Modern Playwright-based scraper
- **`analyze_catalog.py`** - Pre-scraping analysis tool (no dependencies)

### Setup Files
- **`requirements.txt`** - Python package dependencies
- **`setup_scraper.bat`** - Windows setup script
- **`setup_scraper.sh`** - Linux/Mac setup script

## 🔍 Approach Comparison

| Tool | Best For | Pros | Cons |
|------|----------|------|------|
| **Selenium** | CTCLink, PeopleSoft systems | Very compatible, handles complex JS | Slower, needs Chrome |
| **Playwright** | Modern SPAs, fast scraping | Fast, modern, good debugging | Less compatible with old systems |
| **Analysis Tool** | Understanding site structure | No dependencies, quick insights | Limited to static analysis |

## 🛠️ Scraping Strategy for CTCLink

Based on analysis of CTCLink systems, the recommended approach:

### 1. **Pre-Analysis Phase**
```python
# Run analyze_catalog.py first to understand:
python analyze_catalog.py
```
- Identifies JavaScript frameworks
- Finds iframes and forms
- Locates potential API endpoints
- Recommends best scraping approach

### 2. **Main Scraping Phase**
```python
# For CTCLink systems, use Selenium:
scraper = CourseScraperCTCLink(headless=False)  # Set True for production
success = scraper.scrape_full_catalog(catalog_url)
```

### 3. **Key CTCLink Challenges**
- **College navigation**: Automatically finds and clicks Olympic College link
- **iframes**: Most content is in `main_iframe`
- **Dynamic loading**: Content loads via JavaScript
- **Form interactions**: Need to select subjects/terms
- **Session management**: May require login for full access
- **Debugging**: Screenshots automatically saved at key steps

## 📊 Data Output

Both scrapers output data in multiple formats:

### JSON Format
```json
{
  "course_code": "CS 101",
  "course_title": "Introduction to Computer Science",
  "credits": "3",
  "instructor": "Dr. Smith",
  "schedule": "MWF 10:00-11:00",
  "location": "Room 101",
  "raw_text": "...",
  "extracted_at": "2025-09-30T12:00:00"
}
```

### CSV Format
Suitable for Excel analysis and database import.

## 🔧 Configuration Options

### Selenium Scraper Options
```python
scraper = CourseScraperCTCLink(
    headless=True,        # Run without browser window
    wait_timeout=10       # Max wait time for elements
)
```

### Playwright Scraper Options
```python
scraper = CourseScraperPlaywright(
    headless=True         # Run without browser window
)
```

## 🚨 Common Issues & Solutions

### Issue: "Chrome driver not found"
**Solution:** 
- Install Chrome browser
- Selenium 4+ includes automatic driver management
- Or manually install: `pip install webdriver-manager`

### Issue: "No course data found"
**Solutions:**
1. Set `headless=False` to see what's happening
2. Check if login is required
3. Verify the iframe is being accessed
4. Check for CAPTCHA or bot detection

### Issue: "Timeout waiting for elements"
**Solutions:**
1. Increase `wait_timeout` parameter
2. Check internet connection
3. Verify the site is accessible
4. The site might be blocking automated access

### Issue: "Import errors"
**Solution:** Run the setup script:
```bash
# Windows
setup_scraper.bat

# Linux/Mac  
./setup_scraper.sh
```

## 🎯 Customization for Specific Sites

### For Different CTCLink Instances
```python
# Modify these selectors in the scraper:
SUBJECT_SELECTOR = "select[name*='subject']"  # Adjust as needed
SEARCH_BUTTON = "input[type='submit']"        # Adjust as needed
IFRAME_NAME = "main_iframe"                   # May vary by site
```

### For Non-CTCLink Sites
1. Run `analyze_catalog.py` first
2. Modify selectors based on the site's HTML structure
3. Adjust the navigation flow in `scrape_full_catalog()`

## 📈 Performance Tips

1. **Use headless mode** for production: `headless=True`
2. **Limit subjects** for testing: `subjects[:5]` 
3. **Add delays** between requests: `time.sleep(2)`
4. **Handle errors gracefully** with try/catch blocks
5. **Save progress periodically** for long scraping sessions

## 🔍 Debugging Tips

1. **Set headless=False** to watch the browser
2. **Check logs** in `course_scraper.log`
3. **Review auto-screenshots** - saved automatically at key steps:
   - `01_page_loaded.png` - Initial page load
   - `02_olympic_college_page.png` - After clicking Olympic College link
   - `03_inside_iframe.png` - After switching to iframe
   - `04_search_results_[SUBJECT].png` - Search results for each subject
   - `05_scraping_complete.png` - Final state
4. **Use browser dev tools** to inspect elements
5. **Test with a single subject** first

## 📋 Legal and Ethical Considerations

- **Respect robots.txt** and site terms of service
- **Add delays** between requests to avoid overloading servers
- **Consider contacting** the site administrator for API access
- **Check if data is publicly available** through other means
- **Use scraped data responsibly** and according to applicable laws

## 🔗 Useful Resources

- [Selenium Documentation](https://selenium-python.readthedocs.io/)
- [Playwright Documentation](https://playwright.dev/python/)
- [CTCLink User Guides](https://www.sbctc.edu/colleges-staff/it-support/ctclink/)
- [Web Scraping Best Practices](https://blog.apify.com/web-scraping-best-practices/)

## 📞 Support

For issues with this toolkit:
1. Check the generated log files
2. Run `analyze_catalog.py` to understand site structure
3. Try both Selenium and Playwright approaches
4. Check the specific site's documentation or contact their support

---

**Note:** This toolkit is designed for educational and research purposes. Always ensure you have permission to scrape a website and comply with its terms of service.

---

# Original Project Files

## Hello Students! 👋

Welcome to our IS 330 course project! This repository contains example data and resources that will help you learn and practice data analysis concepts throughout the semester.

Feel free to explore, experiment, and don't hesitate to ask questions. Happy learning!
