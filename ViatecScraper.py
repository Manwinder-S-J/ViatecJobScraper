import requests
from bs4 import BeautifulSoup
import json
import time

# URL of the VIATeC job board
viatec_url = "https://members.viatec.ca/job-board/Search?CategoryValues=235246"

# Function to safely make HTTP requests
def safe_request(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return None

# Function to scrape job details
def scrape_job_details(company_page_url):
    response = safe_request(company_page_url)
    if response:
        soup = BeautifulSoup(response.text, 'html.parser')
        company_name = soup.find('h1', class_='gz-pagetitle').text.strip()
        contact_info = soup.find('div', class_='row gz-details-reps')
        contact = contact_info.find('div', class_='gz-member-repname').text.strip()
        contact_title = contact_info.find('div', class_='gz-member-reptitle').text.strip()
        return company_name, contact, contact_title
    else:
        return "N/A", "N/A", "N/A"  # Return placeholder values if scraping fails

# Main scraping function
def scrape_viatec_jobs():
    response = safe_request(viatec_url)
    if not response:
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    jobs_data = []

    for job in soup.find_all('div', class_='card-body gz-content-body'):
        a_tags = job.find_all('a')
        if len(a_tags) < 2:
            continue

        job_position = a_tags[0].text.strip()
        job_url = a_tags[0]['href']
        company_page_url = a_tags[1]['href']

        # Scrape job details with a delay to be respectful
        time.sleep(1)  # Wait for 1 second between requests
        company_name, contact, contact_title = scrape_job_details(company_page_url)

        jobs_data.append({
            'position': job_position,
            'company': company_name,
            'url': job_url,
            'contact': contact,
            'contactTitle': contact_title
        })

    return jobs_data

# Save the scraped data to a JSON file
def save_jobs_to_json(jobs_data, filename='joblist.json'):
    with open(filename, 'w') as file:
        json.dump(jobs_data, file, indent=4)

def main():
    jobs_data = scrape_viatec_jobs()
    if jobs_data:
        save_jobs_to_json(jobs_data)
        print(f"Successfully scraped and saved {len(jobs_data)} job listings.")
    else:
        print("Failed to scrape job listings.")

if __name__ == "__main__":
    main()
