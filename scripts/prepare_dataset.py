import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import re
import time
import json
from pathlib import Path

# Get the base directory of the project
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent
# Create paths to output files
OUTPUT_CSV_PATH = BASE_DIR / "data" / "classifier_data.csv"
OUTPUT_JSON_PATH = BASE_DIR / "data" / "swc_vulnerabilities.json"

def scrape_swc_registry():
    """
    Scrape the SWC Registry to extract vulnerability information.
    """
    base_url = "https://swcregistry.io"
    vulnerabilities = []

    # Set up a session with appropriate headers
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    })

    # First get the main page to find links to all SWC entries
    print("Fetching main page...")
    response = session.get(base_url)

    if response.status_code != 200:
        print(f"Failed to access {base_url}: Status code {response.status_code}")
        return []

    main_soup = BeautifulSoup(response.content, "html.parser")

    # Extract SWC IDs from the navigation links
    swc_links = main_soup.select('a[href^="/docs/SWC-"]')

    if not swc_links:
        print("No SWC links found with initial selector, trying direct approach...")
        swc_ids = [f"SWC-{i}" for i in range(100, 137)]
    else:
        swc_ids = []
        for link in swc_links:
            href = link.get('href', '')
            match = re.search(r'/docs/(SWC-\d+)', href)
            if match:
                swc_ids.append(match.group(1))

    swc_ids = list(dict.fromkeys(swc_ids))
    print(f"Found {len(swc_ids)} SWC IDs to process")

    # Visit each SWC page to extract details
    for swc_id in swc_ids:
        try:
            swc_url = f"{base_url}/docs/{swc_id}/"
            print(f"Scraping {swc_url}")

            swc_response = session.get(swc_url)
            if swc_response.status_code != 200:
                print(f"Failed to access {swc_url}: Status code {swc_response.status_code}")
                continue

            swc_soup = BeautifulSoup(swc_response.content, "html.parser")

            # Extract title
            title = ""
            title_heading = swc_soup.find(lambda tag: tag.name == 'h1' and tag.text.strip() == 'Title')
            if title_heading:
                next_element = title_heading.find_next(['p', 'h2'])
                if next_element.name == 'h2':
                    title = ' '.join(text.strip() for text in title_heading.find_next_siblings(text=True, limit=5)
                                   if text.strip() and not text.parent.name == 'h2')
                else:
                    title = next_element.text.strip()

            # Extract description
            description = ""
            description_heading = swc_soup.find(lambda tag: tag.name == 'h2' and tag.text.strip() == 'Description')
            if description_heading:
                next_element = description_heading.find_next_sibling()
                while next_element and next_element.name != 'h2':
                    if next_element.name == 'p':
                        description += next_element.text.strip() + " "
                    next_element = next_element.find_next_sibling()

            # Extract relationships
            relationships = []
            relationships_heading = swc_soup.find(lambda tag: tag.name == 'h2' and tag.text.strip() == 'Relationships')
            if relationships_heading:
                next_element = relationships_heading.find_next()
                while next_element and next_element.name != 'h2':
                    if next_element.name == 'p':
                        links = next_element.find_all('a')
                        for link in links:
                            relationships.append({"name": link.text.strip(), "url": link.get('href', '')})
                    next_element = next_element.find_next_sibling()

            # Extract remediation
            remediation = ""
            remediation_heading = swc_soup.find(lambda tag: tag.name == 'h2' and tag.text.strip() == 'Remediation')
            if remediation_heading:
                next_element = remediation_heading.find_next_sibling()
                while next_element and next_element.name != 'h2':
                    if next_element.name == 'p':
                        remediation += next_element.text.strip() + " "
                    next_element = next_element.find_next_sibling()

            # Heuristic severity classification based on description
            severity = "Medium"  # Default
            desc_lower = description.lower()
            if "reentrancy" in desc_lower or "drain" in desc_lower or "unauthorized" in desc_lower:
                severity = "High"
            elif "gas" in desc_lower or "unused" in desc_lower or "pragma" in desc_lower:
                severity = "Low"

            vuln_data = {
                "SWC_ID": swc_id,
                "Title": title.strip(),
                "Description": description.strip(),
                "Relationships": [rel["name"] for rel in relationships],
                "Remediation": remediation.strip(),
                "Severity": severity,
                "URL": swc_url
            }

            vulnerabilities.append(vuln_data)
            time.sleep(0.5)

        except Exception as e:
            print(f"Error scraping {swc_id}: {e}")

    return vulnerabilities

if __name__ == "__main__":
    # Create the data directory if it doesn't exist
    OUTPUT_CSV_PATH.parent.mkdir(exist_ok=True)

    print(f"Starting to scrape SWC Registry")
    data = scrape_swc_registry()

    if not data:
        print("No data found. Generating placeholders.")
        data = [{"SWC_ID": f"SWC-{i + 100}",
                 "Title": f"Placeholder Title {i}",
                 "Description": f"Placeholder description for vulnerability {i}",
                 "Relationships": [f"CWE-{i + 600}"],
                 "Severity": "Low",
                 "URL": f"https://swcregistry.io/docs/SWC-{i + 100}/"} for i in range(50)]

    # Save to CSV (with a subset of fields)
    csv_data = [{
        "SWC_ID": item["SWC_ID"],
        "Title": item["Title"],
        "Description": item["Description"],
        "Severity": item["Severity"]
    } for item in data]

    df = pd.DataFrame(csv_data)
    df.to_csv(OUTPUT_CSV_PATH, index=False)
    print(f"Saved {len(data)} entries to {OUTPUT_CSV_PATH}")

    # Save full data to JSON
    with open(OUTPUT_JSON_PATH, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Saved detailed data to {OUTPUT_JSON_PATH}")