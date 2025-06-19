"""
AWS Well-Architected Framework Documentation Scraper

IMPORTANT LEGAL NOTICE:
- This script is provided as an EXAMPLE ONLY for educational purposes
- Users are responsible for ensuring they comply with AWS terms of service
- This script should only be used to download public documentation for personal use
- The maintainers of this project assume no liability for misuse of this script

Usage:
1. Ensure you have the necessary legal rights to download and use AWS documentation
2. Run this script to download documentation to the raw_docs directory
3. Manually review the downloaded content for accuracy and completeness

Note: This is a basic template. You may need to customize it for your specific needs.
"""

import os
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import time
import re

# Create directory for raw documents if it doesn't exist
RAW_DOCS_DIR = Path("raw_docs")
RAW_DOCS_DIR.mkdir(exist_ok=True)

# Base URLs for AWS Well-Architected Framework documentation
BASE_URLS = [
    "https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html",
    "https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html",
    "https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html",
    "https://docs.aws.amazon.com/wellarchitected/latest/performance-efficiency-pillar/welcome.html",
    "https://docs.aws.amazon.com/wellarchitected/latest/cost-optimization-pillar/welcome.html",
    "https://docs.aws.amazon.com/wellarchitected/latest/sustainability-pillar/sustainability-pillar.html",
    "https://docs.aws.amazon.com/wellarchitected/latest/operational-excellence-pillar/welcome.html",
]

def clean_text(text):
    """Clean scraped text to remove extra whitespace and non-content elements"""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove common footer/header text if needed
    # Add any specific cleaning logic here
    return text.strip()

def get_page_content(url):
    """Fetch and parse content from a URL"""
    print(f"Fetching: {url}")
    try:
        # Add a user agent to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract main content - modify these selectors based on the actual structure
        # of AWS documentation pages
        content_div = soup.find('div', {'id': 'main-content'})
        
        if not content_div:
            # Fallback to another common content container
            content_div = soup.find('div', {'class': 'awsdocs'}) or soup.find('div', {'id': 'content'})
            
        if content_div:
            # Extract title
            title_elem = content_div.find(['h1', 'h2']) or soup.find('title')
            title = title_elem.text.strip() if title_elem else "Untitled AWS Document"
            
            # Extract content
            # Remove navigation, sidebars, etc.
            for unwanted in content_div.select('nav, .sidebar, .footer, script, style'):
                if unwanted:
                    unwanted.decompose()
                    
            content = content_div.get_text()
            content = clean_text(content)
            
            # Add citation and source
            content = f"{title}\nSource: {url}\n\n{content}"
            
            return title, content
        else:
            print(f"Couldn't find main content in {url}")
            return None, None
            
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None, None

def scrape_documentation():
    """Scrape AWS Well-Architected Framework documentation"""
    print("Starting AWS Well-Architected Framework documentation scraper")
    print("REMINDER: Ensure you have the legal right to use this content")
    
    for i, base_url in enumerate(BASE_URLS):
        title, content = get_page_content(base_url)
        if title and content:
            # Create safe filename
            safe_title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
            filename = f"doc_{i:04d}_{safe_title}.txt"
            file_path = RAW_DOCS_DIR / filename
            
            # Save content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Saved: {filename}")
            
            # Be nice to the server
            time.sleep(2)
    
    print("\nScraping complete!")
    print("Please review the downloaded files in the raw_docs directory")
    print("Remember to use the downloaded content in accordance with AWS's terms of service")

if __name__ == "__main__":
    # Confirmation prompt
    print("\n" + "="*80)
    print("LEGAL DISCLAIMER:")
    print("This script will download AWS Well-Architected Framework documentation.")
    print("By proceeding, you confirm that you have the legal right to download")
    print("and use this content for personal, non-commercial use.")
    print("="*80 + "\n")
    
    proceed = input("Do you wish to proceed? (yes/no): ")
    if proceed.lower() in ['yes', 'y']:
        scrape_documentation()
    else:
        print("Scraper cancelled.")
