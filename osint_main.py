import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import sys
import time
import re
import json
import csv
import os
import random

# List of user-agents for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0.2 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 10; Pixel 3 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 8.0.0; SM-G950F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
]

# Function to load proxies from a file
def load_proxies(filename):
    proxies = []
    try:
        with open(filename, 'r') as file:
            for line in file:
                proxies.append(line.strip())
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
    return proxies

# Function to clean URL and remove unwanted query parameters
def clean_url(url):
    match = re.search(r'https?://[^\s]+', url)
    if match:
        cleaned_url = match.group(0)
        cleaned_url = re.sub(r'&ved=[^&]+', '', cleaned_url)
        cleaned_url = re.sub(r'&usg=[^&]+', '', cleaned_url)
#        cleaned_url = re.sub(r'^https?://', '', cleaned_url)
#        cleaned_url = re.sub(r'/.*', '', cleaned_url)
        return cleaned_url
    return None

# Function to display a signature in the center of the screen
def show_signature():
    signature = "\n".join([
        "===========================================================================\n"
        "🌐  WELCOME TO OSINT ENGINE  🌐\n"
        "===========================================================================\n"
        "Created by: Afif Hidayatullah\n"
        "Organization: ITSEC Asia\n"
        "Let's find something!!\n"
        "===========================================================================\n"
    ])
    
    terminal_width = os.get_terminal_size().columns
    lines = signature.split('\n')
    centered_signature = "\n".join(line.center(terminal_width) for line in lines)
    print(centered_signature)

# Function to scrape search engine using Selenium
def scrape_search_selenium(engine, query, num_pages=3):
    base_urls = {
        "google": "https://www.google.com/search",
        "bing": "https://www.bing.com/search",
        "duckduckgo": "https://duckduckgo.com/html/"
    }

    if engine not in base_urls:
        print(f"Error: Unsupported search engine '{engine}'")
        return []

    base_url = base_urls[engine]
    found_urls = set()
    collected_results = 0
    total_results = num_pages * 10

    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    for page in range(num_pages):
        search_url = f"{base_url}?q={query}&start={page * 10}"
        driver.get(search_url)
        time.sleep(5)  # Give the page time to load

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        for result in soup.find_all('h3'):
            link = result.find_parent('a')
            if link and 'href' in link.attrs:
                raw_url = link['href']
                cleaned_url = clean_url(raw_url)
                if cleaned_url:
                    found_urls.add(cleaned_url)
                    collected_results += 1

        show_progress(collected_results, total_results)
        time.sleep(random.uniform(10, 15))  # Random delay to avoid detection

    driver.quit()
    return sorted(found_urls)

# Function to scrape Google search results with overall progress
def scrape_search_engine(engine, query, num_pages=3, proxies=[]):
    base_urls = {
        "google": "https://www.google.com/search",
        "bing": "https://www.bing.com/search",
        "duckduckgo": "https://duckduckgo.com/html/"
    }
    
    if engine not in base_urls:
        print(f"Error: Unsupported search engine '{engine}'")
        return []

    base_url = base_urls[engine]
    found_urls = set()
    collected_results = 0
    total_results = num_pages * 10

    for page in range(num_pages):
        params = {
            "q": query,
            "start": page * 10
        }

        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Referer": base_url
        }

        # Bing and DuckDuckGo use slightly different query structures
        if engine == "bing":
            params = {"q": query, "first": page * 10}
        elif engine == "duckduckgo":
            params = {"q": query}

        # Choose a random proxy
        proxies_dict = None
        if proxies:
            proxy = random.choice(proxies)
            proxies_dict = {
                "http": proxy,
                "https": proxy,
            }

        try:
            response = requests.get(base_url, headers=headers, params=params, proxies=proxies_dict, timeout=10)
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            continue

        if response.status_code == 429:  # Rate limit exceeded
            print(f"Rate limit exceeded on {engine}. Waiting to retry...(Please use the proxy menu)")
            time.sleep(60)
            continue
        elif response.status_code != 200:
            print(f"Error: {response.status_code} - Unable to access {engine}.")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')

        for result in soup.find_all('h3'):
            link = result.find_parent('a')
            if link and 'href' in link.attrs:
                raw_url = link['href']
                cleaned_url = clean_url(raw_url)
                if cleaned_url:
                    found_urls.add(cleaned_url)
                    collected_results += 1
	
        show_progress(collected_results, total_results)
	
        # Random delay to avoid detection
        time.sleep(random.uniform(10, 15))

    return sorted(found_urls)
	
# Function to build query based on user choice
def build_query(platform, keyword):
    platform_dorks = {
        "twitter": "(site:twitter.com OR site:x.com)",  # Combine Twitter and X
        "facebook": "site:facebook.com",
        "instagram": "site:instagram.com",
        "github": "site:github.com",
        "postman": "site:postman.com",
        "gdrive": "site:drive.google.com",
        "trello": "site:trello.com",
    }

    if platform == "all":
        query = keyword
    elif platform in platform_dorks:
        query = f"{platform_dorks[platform]} {keyword}"
    else:
        print(f"Unknown platform: {platform}")
        sys.exit(1)

    return query

# Function to display a loading progress bar
def show_progress(collected, total):
    progress = (collected / total) * 100
    bar_length = 40  # Length of the progress bar
    block = int(round(bar_length * progress / 100))
    progress_bar = "█" * block + "-" * (bar_length - block)
    sys.stdout.write(f"\rProgress: [{progress_bar}] {progress:.2f}%")
    sys.stdout.flush()

# Function to display help menu
def show_help():
    help_text = """
Usage: python3 osint_main.py <search_query> [OPTIONS]

Options:
  --platform [twitter|facebook|instagram|all]    Focus search on specific social media platforms.
  --repo [github|postman|all]                    Focus search on repository platforms.
  --drive                                        Focus search on Google Drive files.
  --trello                                       Focus search on Trello boards.
  --proxy [proxy.txt]                            Specify a file containing a list of proxies.
  --bulk [file.txt]                              Load a file with a list of keywords for bulk search.
  --engine [google|bing|duckduckgo]              Choose search engine for scraping (default: Google).
  --output [json|csv|txt]                        Save results in specified format (default: txt).
  --pages [number]                               Specify the number of search result pages to scrape (default: 3).
  --help                                         Show this help menu.

Example:
  python3 osint_main.py "password leak" --platform twitter --engine bing --output json --pages 5
"""
    print(help_text)

# Function to save results in the specified format
def save_results(results, output_format="txt"):
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    
    if output_format == "json":
        filename = f"osint_results_{timestamp}.json"
        with open(filename, 'w') as json_file:
            json.dump(results, json_file, indent=4)
        print(f"\nResults saved to {filename}")
    elif output_format == "csv":
        filename = f"osint_results_{timestamp}.csv"
        with open(filename, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["URL"])
            for result in results:
                writer.writerow([result])
        print(f"\nResults saved to {filename}")
    else:
        filename = f"osint_results_{timestamp}.txt"
        with open(filename, 'w') as txt_file:
            for result in results:
                txt_file.write(result + "\n")
        print(f"\nResults saved to {filename}")

# Main OSINT function
# Main OSINT function
def main():
    if "--help" in sys.argv:
        show_help()
        return

    if len(sys.argv) < 2:
        print("Error: Missing search query.")
        show_help()
        sys.exit(1)

    # Initialize variables
    search_query = None  # Start with None to differentiate single search vs. bulk
    platform = "all"
    output_format = "txt"
    engine = "google"
    num_pages = 3
    proxy_file = None
    bulk_file = None
    proxies = []

    # Parse command-line arguments
    for arg in sys.argv[1:]:  # Start from index 1 to exclude the script name
        if arg.startswith("--platform"):
            platform = sys.argv[sys.argv.index(arg) + 1]
        elif arg.startswith("--output"):
            output_format = sys.argv[sys.argv.index(arg) + 1]
        elif arg.startswith("--engine"):
            engine = sys.argv[sys.argv.index(arg) + 1]
        elif arg.startswith("--pages"):
            num_pages = int(sys.argv[sys.argv.index(arg) + 1])
        elif arg.startswith("--proxy"):
            proxy_file = sys.argv[sys.argv.index(arg) + 1]
        elif arg.startswith("--bulk"):
            bulk_file = sys.argv[sys.argv.index(arg) + 1]

    # Load proxies if provided
    if proxy_file:
        proxies = load_proxies(proxy_file)

    # Perform bulk search if bulk file is provided
    if bulk_file:
        try:
            with open(bulk_file, 'r') as file:
                keywords = [line.strip() for line in file.readlines() if line.strip()]  # Skip empty lines
        except FileNotFoundError:
            print(f"Error: Bulk file '{bulk_file}' not found.")
            sys.exit(1)

        all_results = []
        for keyword in keywords:
            print(f"\nSearching for keyword: {keyword}")
            query = build_query(platform, keyword)  # Build query with the current keyword
            results = scrape_search_engine(engine, query, num_pages, proxies)
            all_results.extend(results)

        save_results(all_results, output_format)
    else:
        # Perform single search
        search_query = sys.argv[1]  # Use the first argument as the search query
        query = build_query(platform, search_query)
        results = scrape_search_engine(engine, query, num_pages, proxies)
        save_results(results, output_format)

if __name__ == "__main__":
    # Show signature
    show_signature()
    main()
