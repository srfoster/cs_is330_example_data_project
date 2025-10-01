@echo off
REM Course Catalog Scraper Setup Script for Windows
REM This script installs all required dependencies for scraping dynamic course catalogs

echo === Course Catalog Scraper Setup ===
echo.

REM Install Python packages
echo Installing Python packages...
pip install selenium playwright requests beautifulsoup4 pandas

echo.
echo Installing Playwright browsers...
playwright install chromium

echo.
echo === Setup Complete ===
echo.
echo Available scraping options:
echo 1. Selenium (course_catalog_scraper.py) - Most compatible
echo 2. Playwright (course_catalog_scraper_playwright.py) - Modern, faster
echo.
echo To run the scrapers:
echo   python course_catalog_scraper.py
echo   python course_catalog_scraper_playwright.py
echo.
echo Note: Make sure Chrome browser is installed for Selenium
pause