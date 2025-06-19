import trafilatura
from bs4 import BeautifulSoup
import requests
from pathlib import Path
import urllib.parse
from tqdm import tqdm
import time
import re

class DocumentScraper:
    def __init__(self, base_urls, output_dir="./raw_docs", delay=1.0):
        self.base_urls = base_urls
        self.out_dir = Path(output_dir)
        self.out_dir.mkdir(exist_ok=True)
        self.processed_urls = set()  # Track URLs we've already processed
        self.delay = delay  # Delay between requests to avoid overloading servers
        self.doc_counter = 0
    
    def extract_content(self, url):
        """Extract content from a URL using trafilatura or BeautifulSoup as fallback"""
        try:
            resp = requests.get(url, timeout=10)
            html = resp.text
            # Use trafilatura to extract main content
            text = trafilatura.extract(html)
            if not text:
                # Fallback to BeautifulSoup
                print(f"Trafilatura couldn't extract content from {url}, falling back to BeautifulSoup")
                soup = BeautifulSoup(html, "html.parser")
                text = soup.get_text(separator=' ', strip=True)
            
            return html, text
        except Exception as e:
            print(f"Error extracting content from {url}: {e}")
            return None, None
    
    def find_child_urls(self, parent_url, html):
        """Find relevant child URLs in the HTML content"""
        if not html:
            return []
            
        # Parse HTML
        soup = BeautifulSoup(html, "html.parser")
        base_url_parts = urllib.parse.urlparse(parent_url)
        base_domain = f"{base_url_parts.scheme}://{base_url_parts.netloc}"
        base_path = base_url_parts.path.rsplit('/', 1)[0] if '/' in base_url_parts.path else ''
        
        # Extract all links
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            
            # Handle relative URLs
            if href.startswith('/'):
                full_url = f"{base_domain}{href}"
            elif not href.startswith(('http://', 'https://')):
                full_url = f"{base_domain}{base_path}/{href}"
            else:
                full_url = href
                
            # Filter for relevant links (same domain and not anchors)
            parsed = urllib.parse.urlparse(full_url)
            
            # Skip irrelevant links
            if (parsed.netloc == base_url_parts.netloc and  # Same domain
                not href.startswith('#') and  # Not an anchor
                '.html' in href):  # HTML page
                links.append(full_url)
                
        return links
    
    def save_content(self, url, text):
        """Save extracted content to file"""
        if not text:
            return
            
        # Create a filename based on the URL path
        url_parts = urllib.parse.urlparse(url)
        path_parts = url_parts.path.strip('/').split('/')
        url_slug = '-'.join(path_parts).replace('.html', '')
        
        # Limit filename length and ensure it's valid
        if url_slug:
            url_slug = re.sub(r'[^\w\-]', '_', url_slug)[:50]  # Remove invalid chars and limit length
            filename = f"doc_{self.doc_counter:04d}_{url_slug}.txt"
        else:
            filename = f"doc_{self.doc_counter:04d}.txt"
            
        self.doc_counter += 1
        
        # Save the content
        output_file = self.out_dir / filename
        output_file.write_text(text[:1_000_000], encoding="utf-8")  # Cap size at 1MB
        print(f"Saved {output_file} ({len(text)} characters)")
        
        return filename
    
    def process_url(self, url, max_depth=2, current_depth=0):
        """Process a URL and its children recursively"""
        # Check if we've already processed this URL
        if url in self.processed_urls:
            return
            
        # Add to processed set
        self.processed_urls.add(url)
        print(f"Processing {url} (depth {current_depth})")
        
        # Respect politeness delay
        time.sleep(self.delay)
        
        # Extract content
        html, text = self.extract_content(url)
        
        # Save content if extracted successfully
        if text:
            self.save_content(url, text)
        
        # Stop recursion if we've reached max depth
        if current_depth >= max_depth:
            return
            
        # Find and process child URLs
        child_urls = self.find_child_urls(url, html)
        if child_urls:
            print(f"Found {len(child_urls)} child URLs for {url}")
            for child_url in child_urls:
                if child_url not in self.processed_urls:
                    self.process_url(child_url, max_depth, current_depth + 1)
    
    def run(self, max_depth=2):
        """Process all base URLs"""
        print(f"Starting document scraping, output dir: {self.out_dir}")
        print(f"Will follow links to a maximum depth of {max_depth}")
        
        for url in self.base_urls:
            url = url.strip()
            if url:  # Skip empty lines
                self.process_url(url, max_depth)
                
        print(f"\nScraping complete. Processed {len(self.processed_urls)} URLs and saved {self.doc_counter} documents.")

# Main execution
if __name__ == "__main__":
    # Read base URLs from file
    with open("doc_urls.txt") as f:
        base_urls = [line.strip() for line in f if line.strip()]
    
    # Create and run the scraper
    scraper = DocumentScraper(base_urls)
    scraper.run(max_depth=2)  # Follow links up to 2 levels deep