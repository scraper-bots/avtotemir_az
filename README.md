# Avtotemir.az Web Scraper

A Python web scraper for extracting master mechanic profiles from [avtotemir.az](https://avtotemir.az).

## Features

- Scrapes all master listings from paginated pages
- Extracts detailed profile information for each master
- Retrieves phone numbers from the contact endpoint
- Saves data in both CSV and JSON formats
- Includes rate limiting to be respectful to the server
- Comprehensive logging for monitoring progress

## Data Extracted

For each master mechanic, the scraper collects:

- **Basic Information**: Name, ID, URL
- **Professional Details**: Position/profession, car brands serviced
- **Location**: City and district
- **Ratings**: Rating score and number of votes
- **Statistics**: Years of experience, profile views, date added
- **Contact**: Phone numbers, full address
- **Services**: All services offered and applicable car brands
- **Media**: Profile and gallery images
- **Description**: Notes and additional information

## Installation

1. Clone or download this repository

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the scraper with default settings (scrapes up to 100 pages):

```bash
python scraper.py
```

### Custom Configuration

Edit the `main()` function in `scraper.py` to customize:

```python
def main():
    scraper = AvtotemirScraper()

    # Customize these parameters:
    scraper.scrape_all_pages(
        start_page=1,      # Start from page 1
        max_pages=50       # Scrape maximum 50 pages
    )

    # Save results
    scraper.save_to_json('avtotemir_masters.json')
    scraper.save_to_csv('avtotemir_masters.csv')
```

### Programmatic Usage

You can also use the scraper as a module:

```python
from scraper import AvtotemirScraper

# Create scraper instance
scraper = AvtotemirScraper()

# Scrape specific page range
scraper.scrape_all_pages(start_page=1, end_page=10)

# Access scraped data
for master in scraper.masters_data:
    print(f"{master['name']} - {master['position']}")

# Save to files
scraper.save_to_json('output.json')
scraper.save_to_csv('output.csv')
```

## Output Files

### JSON Format (`avtotemir_masters.json`)

Structured JSON with nested arrays for services, phone numbers, and images:

```json
[
  {
    "id": "4540",
    "name": "Elmin Zeynili",
    "position": "Mühərrikçi-benzin",
    "car_brands": "Bütün markalar",
    "location": "Bakı, Suraxanı",
    "rating": "4.6",
    "votes": "9",
    "phone_numbers": ["051 605-04-44", "070 618-04-44"],
    "services": [
      {
        "position": "Mühərrikçi-benzin",
        "car": "Bütün markalar"
      }
    ],
    ...
  }
]
```

### CSV Format (`avtotemir_masters.csv`)

Flattened data with semicolon-separated values for lists:

| id | name | position | car_brands | phone_numbers | ... |
|----|------|----------|------------|---------------|-----|
| 4540 | Elmin Zeynili | Mühərrikçi-benzin | Bütün markalar | 051 605-04-44; 070 618-04-44 | ... |

## Rate Limiting

The scraper includes built-in delays to be respectful to the server:
- 1 second between individual master profiles
- 2 seconds between pages
- 0.5 seconds when fetching phone numbers

## Logging

The scraper provides detailed logging output:
- Info: Progress updates and successful operations
- Warning: Empty pages or missing data
- Error: Request failures or parsing errors

## Error Handling

- Automatically retries failed requests
- Continues scraping even if individual profiles fail
- Stops after 3 consecutive empty pages (indicates end of listings)

## Notes

- The scraper uses a session with proper headers to mimic browser requests
- All text is saved in UTF-8 encoding to preserve Azerbaijani characters
- The scraper automatically detects when it has reached the end of available pages

## Legal and Ethical Considerations

This scraper is for educational and research purposes only. When using this tool:
- Respect the website's terms of service
- Do not overload the server with excessive requests
- Use the data responsibly and ethically
- Consider reaching out to the website owners if you need large-scale data access

## Troubleshooting

**Issue**: Scraper stops early
- Check your internet connection
- The website may have rate limiting - increase delays in the code

**Issue**: Missing phone numbers
- Phone numbers require a separate API call - ensure your IP isn't blocked
- Check the logs for specific error messages

**Issue**: Encoding errors in CSV
- Ensure you're opening the CSV file with UTF-8 encoding
- Use Excel's "Import from CSV" feature with UTF-8 encoding

## License

This project is provided as-is for educational purposes.
