import os
import shutil
import random
import time
import argparse
import requests
import json
import csv
import sys
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Function to display the banner centered
def show_banner():
    banner = """
===========================================================================
                           🌐  WELCOME TO OSINT ENGINE  🌐
===========================================================================
                      Created by: Afif Hidayatullah
                      Organization: ITSEC Asia
                      Let's find something!!
===========================================================================
"""
    terminal_width = os.get_terminal_size().columns
    centered_banner = "\n".join(line.center(terminal_width) for line in banner.split("\n"))
    print(centered_banner)

# Function to build query based on platform (optional)
def build_query(platform, keyword):
    platform_dorks = {
        "twitter": "(site:twitter.com OR site:x.com)",
        "facebook": "site:facebook.com",
        "instagram": "site:instagram.com",
        "github": "site:github.com",
        "postman": "site:postman.com",
        "gdrive": "site:drive.google.com",
        "trello": "site:trello.com",
    }

    # Jika platform tidak diberikan, langsung gunakan keyword
    if not platform:
        return keyword

    # Jika platform valid, gunakan query dengan dorking
    if platform in platform_dorks:
        return f"{platform_dorks[platform]} {keyword}"

    return keyword

# Function to display a loading progress bar
def show_progress(collected, total):
    progress = (collected / total) * 100 if total > 0 else 0
    bar_length = 40
    filled_length = int(bar_length * progress / 100)
    progress_bar = "█" * filled_length + "-" * (bar_length - filled_length)
    sys.stdout.write(f"\rProgress: [{progress_bar}] {progress:.2f}%")
    sys.stdout.flush()

# Function to close all existing Chrome processes
def kill_existing_chrome():
    print("🛑 Closing existing Chrome processes...")
    try:
        os.system("pkill -f chrome")
        os.system("taskkill /F /IM chrome.exe /T")
    except:
        pass
    time.sleep(2)

# Function to create a unique user-data directory for Selenium
def get_unique_user_data_dir():
    base_dir = "/tmp/selenium_profiles"
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    unique_dir = os.path.join(base_dir, f"profile_{random.randint(10000, 99999)}")

    if os.path.exists(unique_dir):
        shutil.rmtree(unique_dir)

    os.makedirs(unique_dir, exist_ok=True)
    return unique_dir

# Function to clean extracted URLs (remove unwanted Google redirects)
def clean_url(url):
    # Menghapus URL yang berasal dari Google atau akun login
    if "google.com" in url or "accounts.google.com" in url:
        return None

    # Membersihkan parameter dari Google Search redirect
    url = url.split("&")[0]

    return url

# Function to scrape search results using Selenium
def scrape_search_selenium(engine, query, num_pages=3):
    base_urls = {
        "google": "https://www.google.com/search",
        "bing": "https://www.bing.com/search",
        "duckduckgo": "https://duckduckgo.com/html/"
    }

    if engine not in base_urls:
        print(f"❌ Error: Unsupported search engine '{engine}'")
        return []

    base_url = base_urls[engine]
    found_urls = set()

    # Kill existing Chrome processes
    kill_existing_chrome()

    # Setup Selenium WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument(f"user-agent=Mozilla/5.0")

    # Use unique user-data-dir
    user_data_dir = get_unique_user_data_dir()
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")

    print(f"🚀 Initializing Selenium WebDriver... (User-Data: {user_data_dir})")
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    except Exception as e:
        print(f"❌ Selenium WebDriver Error: {e}")
        return []

    print("\n🔍 Scraping search results...\n")

    total_pages = num_pages * 10
    collected_results = 0

    for page in range(num_pages):
        search_url = f"{base_url}?q={query.replace(' ', '+')}&start={page * 10}"
        driver.get(search_url)

        time.sleep(random.uniform(3, 5))
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(3, 5))

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        for result in soup.find_all('a', href=True):
            raw_url = result['href']
            if raw_url.startswith('/url?q='):
                cleaned_url = clean_url(raw_url.split('/url?q=')[1].split('&')[0])
                if cleaned_url:
                    found_urls.add(cleaned_url)
                    collected_results += 1
                    show_progress(collected_results, total_pages)

        time.sleep(random.uniform(10, 15))

    driver.quit()
    return sorted(found_urls)

# Function to save results in a file
def save_results(results, output_format, filename):
    if not results:
        print("\n❌ No results found.")
        return

    filepath = f"{filename}.{output_format}"

    if output_format == "json":
        with open(filepath, "w") as json_file:
            json.dump(results, json_file, indent=4)
    elif output_format == "csv":
        with open(filepath, "w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["URL"])
            for result in results:
                writer.writerow([result])
    else:
        with open(filepath, "w") as txt_file:
            for result in results:
                txt_file.write(result + "\n")

    print(f"\n✅ Results saved to {filepath}")

# Main function
def main():
    show_banner()

    parser = argparse.ArgumentParser(description="OSINT Engine for Web Scraping")
    parser.add_argument("query", nargs="+", help="Search query")
    parser.add_argument("--platform", choices=["twitter", "facebook", "instagram", "github", "postman", "gdrive", "trello", "all"], help="Search specific social media (optional)")
    parser.add_argument("--engine", default="google", choices=["google", "bing", "duckduckgo"], help="Search engine")
    parser.add_argument("--output", default="txt", choices=["json", "csv", "txt"], help="Output format")
    parser.add_argument("--filename", default="results", help="Filename to save results")
    parser.add_argument("--pages", type=int, default=3, help="Number of search result pages")

    args = parser.parse_args()

    # Gunakan `build_query` hanya jika user memasukkan `--platform`
    search_query = build_query(args.platform, " ".join(args.query))

    print(f"\n🔍 Searching: {search_query} on {args.engine} ({args.pages} pages)")

    results = scrape_search_selenium(args.engine, search_query, args.pages)

    save_results(results, args.output, args.filename)

if __name__ == "__main__":
    main()
