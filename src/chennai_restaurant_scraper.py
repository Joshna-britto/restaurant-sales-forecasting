
import csv
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

URL = "https://www.livechennai.com/saravanabhavan_hotel_menu_price_list.asp"
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs" / "chennai_restaurant_menu.csv"
USER_AGENT = "StudentAcademicProject/1.0"

# Check the site's robots.txt before scraping
parts = urlparse(URL)
robots_url = f"{parts.scheme}://{parts.netloc}/robots.txt"

try:
    robots_response = requests.get(
        robots_url,
        headers={"User-Agent": USER_AGENT},
        timeout=15
    )
except requests.RequestException as exc:
    raise SystemExit(f"Could not check robots.txt: {exc}")

if robots_response.status_code == 404:
    print("robots.txt was not found; checking the site's published terms.")
elif robots_response.status_code != 200:
    raise SystemExit(
        f"Could not verify robots.txt (HTTP "
        f"{robots_response.status_code}). Stopped."
    )
else:
    parser = RobotFileParser()
    parser.parse(robots_response.text.splitlines())
    if not parser.can_fetch(USER_AGENT, URL):
        raise SystemExit("robots.txt disallows this page. Stopped.")

# Check the site's terms before continuing.
# If the terms prohibit automated collection, stop here.

response = requests.get(
    URL,
    headers={"User-Agent": USER_AGENT},
    timeout=20
)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")
records = []
category = "Uncategorized"

# Extract text from page tables and other visible page elements.
for element in soup.find_all(["tr", "p", "li"]):
    text = element.get_text(" ", strip=True)
    if not text:
        continue

    cells = [
        cell.get_text(" ", strip=True)
        for cell in element.find_all(["td", "th"])
    ]

    if len(cells) >= 2:
        item = cells[0].strip()
        price_text = " ".join(cells[1:])
    else:
        # Some pages display items and prices as text rather than tables.
        match = re.search(
            r"(.+?)\s*[|:-]\s*(?:₹|Rs\.?\s*)?([\d,]+(?:\.\d{1,2})?)\s*$",
            text,
            re.IGNORECASE
        )
        if not match:
            continue
        item, price_text = match.groups()

    price_match = re.search(
        r"(?:₹|Rs\.?\s*)?([\d,]+(?:\.\d{1,2})?)",
        price_text,
        re.IGNORECASE
    )
    if not price_match:
        continue

    item = item.strip(" |:-\t")
    if not item or item.lower() in {
        "food items", "price", "price (rs)", "saravana bhavan"
    }:
        continue

    price = float(price_match.group(1).replace(",", ""))

    # Skip obvious page headings or implausible prices.
    if len(item) > 100 or price <= 0 or price > 10000:
        continue

    records.append({
        "restaurant": "Saravana Bhavan",
        "city": "Chennai",
        "category": category,
        "dish": item,
        "price_inr": price,
        "source_url": URL,
        "collected_date": date.today().isoformat()
    })

# Remove duplicate rows
unique = {}
for record in records:
    key = (record["dish"].lower(), record["price_inr"])
    unique[key] = record

records = list(unique.values())
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

if not records:
    raise SystemExit(
        "No menu records were extracted. Inspect the page HTML "
        "before changing the extraction rules."
    )

with OUTPUT.open("w", newline="", encoding="utf-8-sig") as file:
    writer = csv.DictWriter(file, fieldnames=records[0].keys())
    writer.writeheader()
    writer.writerows(records)

print("Extracted menu records:", len(records))
print("Saved CSV:", OUTPUT)
print("Sample rows:")
for record in records[:5]:
    print(record)
