"""
Simple Course Catalog Analysis Script
This script demonstrates basic web scraping without heavy dependencies
"""

import requests
from datetime import datetime
import json
import re
import time

class SimpleCatalogAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.data = []
        
    def analyze_catalog_structure(self, url):
        """
        Analyze the catalog structure without JavaScript execution
        This helps understand what we're dealing with
        """
        try:
            print(f"Analyzing catalog structure: {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            html_content = response.text
            
            # Analyze the HTML structure
            analysis = {
                'url': url,
                'status_code': response.status_code,
                'content_length': len(html_content),
                'analysis_time': datetime.now().isoformat(),
                'findings': {}
            }
            
            # Look for common elements
            patterns = {
                'forms': r'<form[^>]*>',
                'iframes': r'<iframe[^>]*>',
                'scripts': r'<script[^>]*>',
                'select_elements': r'<select[^>]*>',
                'links': r'<a[^>]*href=["\'][^"\']*["\'][^>]*>',
                'course_mentions': r'course|class|catalog',
                'search_elements': r'search|browse|find'
            }
            
            for name, pattern in patterns.items():
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                analysis['findings'][name] = {
                    'count': len(matches),
                    'samples': matches[:3] if matches else []
                }
                
            # Look for JavaScript frameworks
            js_frameworks = {
                'jQuery': r'jquery',
                'React': r'react',
                'Angular': r'angular',
                'Vue': r'vue\.js',
                'CTCLink': r'ctclink',
                'PeopleSoft': r'peoplesoft|ps_'
            }
            
            analysis['frameworks'] = {}
            for framework, pattern in js_frameworks.items():
                if re.search(pattern, html_content, re.IGNORECASE):
                    analysis['frameworks'][framework] = True
                    
            # Extract potential API endpoints or form actions
            form_actions = re.findall(r'action=["\']([^"\']*)["\']', html_content, re.IGNORECASE)
            analysis['form_actions'] = form_actions[:10]  # Limit to first 10
            
            # Look for AJAX/API calls in JavaScript
            api_patterns = [
                r'\.ajax\([^)]*\)',
                r'fetch\([^)]*\)',
                r'XMLHttpRequest',
                r'/api/[^"\'\s]*',
                r'/service/[^"\'\s]*'
            ]
            
            analysis['potential_apis'] = []
            for pattern in api_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                analysis['potential_apis'].extend(matches[:5])
                
            return analysis
            
        except requests.RequestException as e:
            return {'error': f"Request failed: {e}", 'url': url}
        except Exception as e:
            return {'error': f"Analysis failed: {e}", 'url': url}
            
    def extract_static_links(self, url):
        """Extract all links that might lead to course data"""
        try:
            response = self.session.get(url, timeout=30)
            html_content = response.text
            
            # Find all links
            link_pattern = r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>([^<]*)</a>'
            links = re.findall(link_pattern, html_content, re.IGNORECASE)
            
            course_related_links = []
            keywords = ['course', 'class', 'catalog', 'browse', 'search', 'schedule', 'program']
            
            for href, text in links:
                if any(keyword in text.lower() or keyword in href.lower() for keyword in keywords):
                    course_related_links.append({
                        'url': href,
                        'text': text.strip(),
                        'full_url': self._resolve_url(url, href)
                    })
                    
            return course_related_links
            
        except Exception as e:
            print(f"Error extracting links: {e}")
            return []
            
    def _resolve_url(self, base_url, relative_url):
        """Resolve relative URLs to absolute URLs"""
        from urllib.parse import urljoin
        return urljoin(base_url, relative_url)
        
    def generate_scraping_strategy(self, analysis):
        """Generate a recommended scraping strategy based on analysis"""
        strategy = {
            'recommended_approach': 'selenium',  # Default
            'reasons': [],
            'specific_steps': [],
            'challenges': [],
            'alternatives': []
        }
        
        # Analyze findings to recommend approach
        if analysis.get('findings', {}).get('iframes', {}).get('count', 0) > 0:
            strategy['challenges'].append('Site uses iframes - need to switch context')
            
        if analysis.get('findings', {}).get('scripts', {}).get('count', 0) > 10:
            strategy['reasons'].append('Heavy JavaScript usage detected')
            
        if 'PeopleSoft' in analysis.get('frameworks', {}):
            strategy['reasons'].append('PeopleSoft/CTCLink system detected')
            strategy['specific_steps'].extend([
                'Navigate to main catalog page',
                'Switch to iframe if present',
                'Look for subject/department dropdowns',
                'Iterate through subjects to get course listings',
                'Handle pagination if present'
            ])
            
        if analysis.get('findings', {}).get('forms', {}).get('count', 0) > 0:
            strategy['specific_steps'].append('Interact with search forms')
            
        # Recommend alternatives
        strategy['alternatives'] = [
            'Playwright - Better for modern SPAs',
            'Requests + BeautifulSoup - If content is server-rendered',
            'API endpoints - If available and discoverable'
        ]
        
        return strategy
        
    def save_analysis(self, analysis, filename=None):
        """Save analysis results to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"catalog_analysis_{timestamp}.json"
            
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
            
        print(f"Analysis saved to: {filename}")
        return filename

# Example usage and demonstration
if __name__ == "__main__":
    analyzer = SimpleCatalogAnalyzer()
    
    catalog_url = "https://csprd.ctclink.us/psp/csprd/EMPLOYEE/SA/s/WEBLIB_HCX_CM.H_COURSE_CATALOG.FieldFormula.IScript_Main"
    
    print("=== Course Catalog Analysis ===")
    print()
    
    # Analyze the catalog structure
    print("1. Analyzing catalog structure...")
    analysis = analyzer.analyze_catalog_structure(catalog_url)
    
    print(f"   Status Code: {analysis.get('status_code', 'Error')}")
    print(f"   Content Length: {analysis.get('content_length', 0)} characters")
    
    if 'findings' in analysis:
        print(f"   Forms found: {analysis['findings']['forms']['count']}")
        print(f"   iframes found: {analysis['findings']['iframes']['count']}")
        print(f"   Scripts found: {analysis['findings']['scripts']['count']}")
        
    if 'frameworks' in analysis:
        detected = [fw for fw, present in analysis['frameworks'].items() if present]
        if detected:
            print(f"   Frameworks detected: {', '.join(detected)}")
    
    print()
    
    # Extract relevant links
    print("2. Extracting course-related links...")
    links = analyzer.extract_static_links(catalog_url)
    print(f"   Found {len(links)} relevant links:")
    for i, link in enumerate(links[:5], 1):
        print(f"     {i}. {link['text']} -> {link['url']}")
    
    print()
    
    # Generate scraping strategy
    print("3. Generating scraping strategy...")
    strategy = analyzer.generate_scraping_strategy(analysis)
    print(f"   Recommended approach: {strategy['recommended_approach'].upper()}")
    
    if strategy['reasons']:
        print("   Reasons:")
        for reason in strategy['reasons']:
            print(f"     - {reason}")
            
    if strategy['challenges']:
        print("   Challenges:")
        for challenge in strategy['challenges']:
            print(f"     - {challenge}")
    
    print()
    print("4. Recommended steps:")
    for i, step in enumerate(strategy['specific_steps'], 1):
        print(f"   {i}. {step}")
    
    # Save analysis
    print()
    filename = analyzer.save_analysis(analysis)
    
    print()
    print("=== Next Steps ===")
    print("1. Run setup_scraper.bat to install dependencies")
    print("2. Use course_catalog_scraper.py (Selenium) for most reliable results")
    print("3. Try course_catalog_scraper_playwright.py for faster execution")
    print("4. Check the generated analysis file for detailed findings")