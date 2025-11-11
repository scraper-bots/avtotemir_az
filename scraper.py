#!/usr/bin/env python3
"""
Avtotemir.az Web Scraper
Scrapes master mechanic profiles from avtotemir.az
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
import re
import time
from typing import Dict, List, Optional
from urllib.parse import urljoin
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AvtotemirScraper:
    """Scraper for avtotemir.az master profiles"""

    BASE_URL = "https://avtotemir.az"
    ALL_URL = f"{BASE_URL}/all"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8,ru;q=0.7,az;q=0.6',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'DNT': '1',
            'Referer': self.BASE_URL,
        })
        self.masters_data = []

    def get_page_listings(self, page: int) -> Optional[str]:
        """
        Fetch listings HTML from a specific page

        Args:
            page: Page number to fetch

        Returns:
            HTML content or None if request fails
        """
        try:
            logger.info(f"Fetching page {page}...")
            # Add AJAX headers for this endpoint
            headers = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'X-Requested-With': 'XMLHttpRequest',
            }
            response = self.session.get(
                self.ALL_URL,
                params={'page': page},
                headers=headers,
                timeout=30
            )
            response.raise_for_status()

            data = response.json()
            return data.get('html', '')

        except requests.RequestException as e:
            logger.error(f"Error fetching page {page}: {e}")
            return None

    def extract_master_links(self, html: str) -> List[Dict[str, str]]:
        """
        Extract master profile links from listing HTML

        Args:
            html: HTML content from listings page

        Returns:
            List of dictionaries with master URLs, IDs, and location
        """
        soup = BeautifulSoup(html, 'html.parser')
        masters = []

        # Find all article elements
        for article in soup.find_all('article'):
            # Find the master profile link
            link = article.find('a', href=re.compile(r'/usta/'))
            if link:
                master_url = link.get('href')
                # Extract master ID from URL or data attributes
                master_id = None
                location = ''

                # Try to find master ID from data-link attributes
                info_link = article.find('a', class_='position open-modal-dialog')
                if info_link and info_link.get('data-link'):
                    match = re.search(r'/usta/(\d+)/info', info_link['data-link'])
                    if match:
                        master_id = match.group(1)

                # Extract location from listing
                location_li = article.find('i', class_=re.compile(r'fa-map-marker'))
                if location_li and location_li.parent:
                    location = location_li.parent.get_text(strip=True)

                masters.append({
                    'url': master_url if master_url.startswith('http') else urljoin(self.BASE_URL, master_url),
                    'id': master_id,
                    'location': location
                })

        logger.info(f"Found {len(masters)} masters on this page")
        return masters

    def get_master_phone(self, master_id: str) -> List[str]:
        """
        Get master's phone numbers from contact endpoint

        Args:
            master_id: Master's ID

        Returns:
            List of phone numbers
        """
        if not master_id:
            return []

        try:
            url = f"{self.BASE_URL}/contact-phone/{master_id}/master"
            # Add AJAX headers for this endpoint
            headers = {
                'Accept': 'text/html, */*; q=0.01',
                'X-Requested-With': 'XMLHttpRequest',
            }
            response = self.session.get(url, headers=headers, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            phones = []

            # Extract phone numbers from href="tel:..." links
            for phone_link in soup.find_all('a', href=re.compile(r'tel:')):
                phone_text = phone_link.get_text(strip=True)
                # Remove icon text and get just the number
                phone_number = re.sub(r'\s+', ' ', phone_text).strip()
                if phone_number:
                    phones.append(phone_number)

            logger.info(f"Found {len(phones)} phone numbers for master {master_id}")
            return phones

        except requests.RequestException as e:
            logger.error(f"Error fetching phone for master {master_id}: {e}")
            return []

    def scrape_master_profile(self, master_url: str, master_id: Optional[str], location: str = '') -> Dict:
        """
        Scrape detailed information from master's profile page

        Args:
            master_url: URL of master's profile
            master_id: Master's ID
            location: Location from listing page

        Returns:
            Dictionary with master's information
        """
        try:
            logger.info(f"Scraping profile: {master_url}")
            response = self.session.get(master_url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            master_data = {
                'url': master_url,
                'id': master_id,
                'name': '',
                'position': '',
                'car_brands': '',
                'location': location,
                'rating': '',
                'votes': '',
                'experience': '',
                'views': '',
                'added_date': '',
                'address': '',
                'note': '',
                'phone_numbers': [],
                'services': [],
                'images': []
            }

            # Extract name
            name_elem = soup.select_one('.master_info .body h2')
            if name_elem:
                master_data['name'] = name_elem.get_text(strip=True)

            # Extract position/profession
            position_elem = soup.select_one('.master_info .body ul li span i.fa-wrench')
            if position_elem and position_elem.parent:
                master_data['position'] = position_elem.parent.get_text(strip=True)

            # Extract car brands
            car_elem = soup.select_one('.master_info .body ul li span i.fa-car')
            if car_elem and car_elem.parent:
                master_data['car_brands'] = car_elem.parent.get_text(strip=True)

            # Extract location
            location_elem = soup.select_one('.master_info .body ul li span i.fa-map-marker-alt')
            if location_elem and location_elem.parent:
                master_data['location'] = location_elem.parent.get_text(strip=True)

            # Extract rating and votes
            rating_elem = soup.select_one('#result')
            if rating_elem:
                rating_text = rating_elem.get_text(strip=True)
                # Parse "4.6 (9 səs)"
                rating_match = re.search(r'([\d.]+)\s*\((\d+)', rating_text)
                if rating_match:
                    master_data['rating'] = rating_match.group(1)
                    master_data['votes'] = rating_match.group(2)

            # Extract experience, views, added date from master_details
            details_main = soup.select_one('.master_details .main')
            if details_main:
                for span in details_main.find_all('span'):
                    text = span.get_text(strip=True)
                    if 'Təcrübə:' in text:
                        master_data['experience'] = text.replace('Təcrübə:', '').strip()
                    elif 'Baxılıb:' in text:
                        master_data['views'] = text.replace('Baxılıb:', '').strip()
                    elif 'Əlavə olundu:' in text:
                        master_data['added_date'] = text.replace('Əlavə olundu:', '').strip()

            # Extract address
            address_elem = soup.select_one('.master_address .marker-link span')
            if address_elem:
                master_data['address'] = address_elem.get_text(strip=True)

            # Extract note/description
            note_elem = soup.select_one('.master_service .text')
            if note_elem:
                # Get all paragraphs and combine them
                note_paragraphs = note_elem.find_all('p')
                master_data['note'] = ' '.join([p.get_text(strip=True) for p in note_paragraphs])

            # Extract services from positions table
            positions_table = soup.select('#positions tbody tr')
            for row in positions_table:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    service = {
                        'position': cells[0].get_text(strip=True),
                        'car': cells[1].get_text(strip=True)
                    }
                    master_data['services'].append(service)

            # Extract images
            for img in soup.select('#master_gallery img'):
                img_src = img.get('src')
                if img_src:
                    master_data['images'].append(img_src)

            # Get phone numbers
            if master_id:
                master_data['phone_numbers'] = self.get_master_phone(master_id)
                time.sleep(0.5)  # Small delay between requests

            logger.info(f"Successfully scraped: {master_data['name']}")
            return master_data

        except requests.RequestException as e:
            logger.error(f"Error scraping profile {master_url}: {e}")
            return {}

    def scrape_all_pages(self, start_page: int = 1, end_page: Optional[int] = None, max_pages: int = 100):
        """
        Scrape all pages of master listings

        Args:
            start_page: Page to start from
            end_page: Page to end at (None for auto-detect)
            max_pages: Maximum number of pages to scrape
        """
        current_page = start_page
        consecutive_empty = 0

        while current_page <= (end_page or start_page + max_pages):
            # Get listings for current page
            html = self.get_page_listings(current_page)

            if not html or not html.strip():
                consecutive_empty += 1
                logger.warning(f"Page {current_page} returned no content ({consecutive_empty} consecutive empty)")

                # If we get 3 consecutive empty pages, assume we've reached the end
                if consecutive_empty >= 3:
                    logger.info(f"Reached end of listings at page {current_page}")
                    break

                current_page += 1
                continue

            # Reset consecutive empty counter
            consecutive_empty = 0

            # Extract master links
            masters = self.extract_master_links(html)

            if not masters:
                logger.warning(f"No masters found on page {current_page}")
                current_page += 1
                continue

            # Scrape each master profile
            for master_info in masters:
                master_data = self.scrape_master_profile(
                    master_info['url'],
                    master_info['id'],
                    master_info.get('location', '')
                )
                if master_data:
                    self.masters_data.append(master_data)

                # Be polite - delay between requests
                time.sleep(1)

            logger.info(f"Completed page {current_page}. Total masters scraped: {len(self.masters_data)}")

            # Delay between pages
            time.sleep(2)
            current_page += 1

        logger.info(f"Scraping completed. Total masters collected: {len(self.masters_data)}")

    def save_to_json(self, filename: str = 'avtotemir_masters.json'):
        """Save scraped data to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.masters_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Data saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving to JSON: {e}")

    def save_to_csv(self, filename: str = 'avtotemir_masters.csv'):
        """Save scraped data to CSV file"""
        if not self.masters_data:
            logger.warning("No data to save")
            return

        try:
            # Flatten the data for CSV
            flattened_data = []
            for master in self.masters_data:
                flat_master = master.copy()
                # Convert lists to strings
                flat_master['phone_numbers'] = '; '.join(master.get('phone_numbers', []))
                flat_master['services'] = '; '.join([
                    f"{s.get('position', '')} ({s.get('car', '')})"
                    for s in master.get('services', [])
                ])
                flat_master['images'] = '; '.join(master.get('images', []))
                flattened_data.append(flat_master)

            # Get all possible fieldnames
            fieldnames = [
                'id', 'name', 'position', 'car_brands', 'location',
                'rating', 'votes', 'experience', 'views', 'added_date',
                'address', 'phone_numbers', 'services', 'note', 'images', 'url'
            ]

            with open(filename, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(flattened_data)

            logger.info(f"Data saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")


def main():
    """Main function to run the scraper"""
    scraper = AvtotemirScraper()

    # Scrape all pages (will auto-detect end)
    scraper.scrape_all_pages(start_page=1, max_pages=1000)

    # Save results
    scraper.save_to_json('avtotemir_masters.json')
    scraper.save_to_csv('avtotemir_masters.csv')

    logger.info("Scraping completed!")


if __name__ == '__main__':
    main()
