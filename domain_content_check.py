import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import argparse
import csv
import json
import socket
import time
import re
from tqdm import tqdm
from bs4 import BeautifulSoup
import os
import sys  # For loading effect
from colorama import init, Fore, Style

# Suppress InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# ANSI escape sequences for coloring text
class Colors:
    GREEN = '\033[92m'  # Keyword found
    RED = '\033[91m'    # Keyword not found
    YELLOW = '\033[93m' # Warning messages
    RESET = '\033[0m'   # Reset to default color

# Function to display Google-like dot loading effect
def display_loading_effect(duration):
    loading_text = "Loading"
    dots = ""
    for _ in range(duration):
        dots += "."
        sys.stdout.write(f"\r{loading_text}{dots}")
        sys.stdout.flush()
        time.sleep(0.5)
        if len(dots) > 3:
            dots = ""  # Reset dots after 3 for continuous effect

# Function to validate domain format
def check_domain_for_keyword(address, keyword, timeout, verify_ssl):
    result_data = {'address': address, 'title_http': '', 'title_https': '', 'ip': '', 'keyword_result': '', 'status_result': ''}
    result_data_for_output = {'address': address, 'title_http': '', 'title_https': '', 'ip': '', 'keyword_result': '', 'status_result': ''}  # For output without symbols

    # Split the URL and path if they exist
    if '/' in address:
        domain, path = address.split('/', 1)
        path = '/' + path
    else:
        domain = address
        path = '/'

    protocols = ['https', 'http']
    responses = {}

    for protocol in protocols:
        try:
            result_data['ip'] = socket.gethostbyname(domain)
            result_data_for_output['ip'] = result_data['ip']
            full_url = f'{protocol}://{domain}{path}'
            response = requests.get(full_url, timeout=timeout, verify=verify_ssl)
            responses[protocol] = response

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                title_tag = soup.title
                title = title_tag.get_text() if title_tag else ''

                if protocol == 'http':
                    result_data['title_http'] = title
                    result_data_for_output['title_http'] = title
                else:
                    result_data['title_https'] = title
                    result_data_for_output['title_https'] = title

                keyword_found = False

                # Check all elements and their attributes for the keyword
                for element in soup.find_all(True):  # True finds all HTML elements
                    # Check the text content of each tag
                    if keyword.lower() in element.get_text().lower():
                        result_data['keyword_result'] = f"✅ Keyword '{keyword}' found in <{element.name}> tag on {address} ({protocol.upper()})"
                        result_data_for_output['keyword_result'] = f"Keyword '{keyword}' found in <{element.name}> tag on {address} ({protocol.upper()})"
                        keyword_found = True
                        break

                    # Check all attributes for the keyword
                    for attr, value in element.attrs.items():
                        if isinstance(value, list):
                            value = ' '.join(value)  # Handle cases where attribute is a list
                        if keyword.lower() in str(value).lower():
                            result_data['keyword_result'] = f"✅ Keyword '{keyword}' found in <{element.name}> tag's '{attr}' attribute on {address} ({protocol.upper()})"
                            result_data_for_output['keyword_result'] = f"Keyword '{keyword}' found in <{element.name}> tag's '{attr}' attribute on {address} ({protocol.upper()})"
                            keyword_found = True
                            break

                    if keyword_found:
                        break

                if not keyword_found:
                    result_data['status_result'] = f"❌ Keyword '{keyword}' not found in {address} ({protocol.upper()})"
                    result_data_for_output['status_result'] = f"Keyword '{keyword}' not found in {address} ({protocol.upper()})"

            elif response.status_code == 404:
                result_data['status_result'] = f"⚠️ Address {address} returned 404 Not Found."
                result_data_for_output['status_result'] = f"Address {address} returned 404 Not Found."
            else:
                result_data['status_result'] = f"⚠️ Address {address} returned status code: {response.status_code}"
                result_data_for_output['status_result'] = f"Address {address} returned status code: {response.status_code}"

        except requests.exceptions.SSLError:
            print(f"⚠️ SSL Error: Trying to access {address} with SSL verification disabled.")
            try:
                response = requests.get(f'{protocol}://{domain}{path}', timeout=timeout, verify=False)
                responses[protocol] = response
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    title_tag = soup.title
                    title = title_tag.get_text() if title_tag else ''

                    if protocol == 'http':
                        result_data['title_http'] = title
                        result_data_for_output['title_http'] = title
                    else:
                        result_data['title_https'] = title
                        result_data_for_output['title_https'] = title

                else:
                    result_data['status_result'] = f"⚠️ Address {address} returned status code: {response.status_code}"
                    result_data_for_output['status_result'] = f"Address {address} returned status code: {response.status_code}"

            except requests.exceptions.RequestException as e:
                result_data['status_result'] = f"⚠️ Failed to access {address} with {protocol}: {e}"
                result_data_for_output['status_result'] = f"Failed to access {address} with {protocol}: {e}"

        except requests.exceptions.RequestException as e:
            result_data['status_result'] = f"⚠️ Failed to access {address} with {protocol}: {e}"
            result_data_for_output['status_result'] = f"Failed to access {address} with {protocol}: {e}"
        except socket.gaierror:
            result_data['status_result'] = f"⚠️ Unable to resolve address: {address}"
            result_data_for_output['status_result'] = f"Unable to resolve address: {address}"

    if result_data['keyword_result']:
        result_data['status_result'] = f"✅ Success"
        result_data_for_output['status_result'] = f"Success"
    else:
        result_data['status_result'] = f"❌ Failed"
        result_data_for_output['status_result'] = f"Failed"

    return result_data, result_data_for_output  # Return both versions


# Modify the check_addresses_in_file function to handle both versions
def check_addresses_in_file(filename, keyword, timeout, verify_ssl):
    results_with_symbols = []
    results_without_symbols = []
    try:
        with open(filename, 'r') as file:
            addresses = file.readlines()
        total_addresses = len(addresses)

        # Progress bar setup
        with tqdm(total=total_addresses, desc="Checking Addresses", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} addresses checked") as pbar:
            for address in addresses:
                address = address.strip()  # Remove extra whitespace/newline
                if address:
                    # Display Google-like loading effect before checking
                    display_loading_effect(3)  # Simulate loading effect for 3 seconds
                    result_data_with_symbols, result_data_without_symbols = check_domain_for_keyword(address, keyword, timeout, verify_ssl)
                    results_with_symbols.append(result_data_with_symbols)
                    results_without_symbols.append(result_data_without_symbols)
                pbar.update(1)
                time.sleep(0.1)  # Simulate processing time for visibility of progress bar

        return results_with_symbols, results_without_symbols  # Return both sets of results
    except FileNotFoundError:
        print(f"🚫 Error: The file {filename} does not exist.")


# Function to print text centered in the terminal
def print_centered(text):
    terminal_width = os.get_terminal_size().columns  # Get the current terminal width
    for line in text.split('\n'):
        print(line.center(terminal_width))

def save_to_csv(results, output_file):
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = results[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(result)

def save_to_json(results, output_file):
    with open(output_file, 'w', encoding='utf-8') as jsonfile:
        json.dump(results, jsonfile, ensure_ascii=False, indent=4)

def main():
    welcome_text = (
        "===========================================================================\n"
        "🌐  WELCOME TO THE DOMAIN CONTENT CHECKER  🌐\n"
        "===========================================================================\n"
        "Created by: Afif Hidayatullah\n"
        "Organization: ITSEC Asia\n"
        "Let's ensure your domains contain the right content!\n"
        "===========================================================================\n"
    )


    print_centered(welcome_text)
    # Setup argument parser
    parser = argparse.ArgumentParser(
        description="Check if addresses in a .txt file (domains or IPs) contain a specific keyword in their HTML content."
    )
    parser.add_argument('filename', type=str, help="Path to the .txt file containing addresses (domains or IPs)")
    parser.add_argument('keyword', type=str, help="Keyword to search for in address content and tags")
    parser.add_argument('--timeout', type=int, default=10, help="Timeout for each address request (default is 10 seconds)")
    parser.add_argument('--output', type=str, help="Output file (CSV or JSON) to save the results")
    parser.add_argument('--ignore-ssl', action='store_true', help="Ignore SSL certificate errors")

    # Parse the command-line arguments
    args = parser.parse_args()

    # Determine whether to verify SSL or not
    verify_ssl = not args.ignore_ssl

    # Read the file and check for the keyword
    results_with_symbols, results_without_symbols = check_addresses_in_file(args.filename, args.keyword, args.timeout, verify_ssl)

    # Save results if an output file is specified
    if args.output:
        if args.output.endswith('.csv'):
            save_to_csv(results_without_symbols, args.output)  # Use the version without symbols
        elif args.output.endswith('.json'):
            save_to_json(results_without_symbols, args.output)  # Use the version without symbols
        else:
            print("🚫 Error: Unsupported file format. Please use .csv or .json.")
    else:
        # If no output file is specified, print results to console
        print("\nResults:")
        for result in results_with_symbols:
            # Print each result in a formatted JSON-like structure with line breaks and indentation
            formatted_result = (
                "{\n"
                f"    'address': '{result['address']}',\n"
                f"    'title_http': '{result['title_http']}',\n"
                f"    'title_https': '{result['title_https']}',\n"
                f"    'ip': '{result['ip']}',\n"
                f"    'keyword_result': \"{result['keyword_result']}\",\n"
                f"    'status_result': \"{result['status_result']}\"\n"
                "}\n"
            )
            print(formatted_result)

if __name__ == "__main__":
    main()