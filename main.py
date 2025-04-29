import os
import logging
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Configure logging
t_logging_format = "%(asctime)s [%(levelname)s] %(message)s"
logging.basicConfig(level=logging.INFO, format=t_logging_format)

# Directory to save output files
OUTPUT_DIR = "./data/"

class ProxyManager:
    """Manages loading and providing proxies from a file."""

    def __init__(self, filepath: str = "proxies.txt"):
        self.filepath = filepath
        self.proxies = self._import_proxies()

    def _import_proxies(self):
        """Imports proxies from the specified file."""
        if not os.path.exists(self.filepath):
            return []
        with open(self.filepath, "r") as f:
            raw_proxies = f.read().splitlines()

        formatted = []
        for proxy in raw_proxies:
            ip, port, user, password = proxy.split(":")
            formatted.append(f"http://{user}:{password}@{ip}:{port}")
        return formatted

    def get_proxy(self, index: int = 0):
        """Returns a proxy by index."""
        return self.proxies[index % len(self.proxies)] if self.proxies else None


def fetch_municipalities():
    """Fetches all municipality names and their URLs from the /gebieden/ page."""
    url = "https://allecijfers.nl/gebieden/"
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'lxml')

    municipalities = []
    for a in soup.find_all('a'):
        text = a.get_text(strip=True)
        if text.startswith('Gemeente '):
            name = text.replace('Gemeente ', '')
            href = a.get('href')
            municipalities.append((name, href))
    logging.info(f"Found {len(municipalities)} municipalities")
    return municipalities


def get_municipality_page(url: str, proxy_manager: ProxyManager) -> str:
    """Downloads the HTML for a municipality page given its URL."""
    proxy = proxy_manager.get_proxy()
    proxies = {'http': proxy, 'https': proxy} if proxy else None
    try:
        resp = requests.get(url, proxies=proxies, timeout=10)
        resp.raise_for_status()
        logging.info(f"Fetched page: {url}")
        return resp.text
    except requests.RequestException as e:
        logging.error(f"Error fetching {url}: {e}")
        return None


def parse_tables(html: str) -> dict:
    """Extracts category tables under the #250-onderwerpen card."""
    soup = BeautifulSoup(html, 'lxml')
    onderwerpen = soup.find('div', id='250-onderwerpen')
    if not onderwerpen:
        logging.error("#250-onderwerpen section not found")
        return {}

    container = onderwerpen.find('div', class_='tab-content')
    if not container:
        logging.error("No tab-content under #250-onderwerpen")
        return {}

    categories = {}
    for pane in container.find_all('div', class_='tab-pane'):
        table = pane.find('table', class_='table table-bordered table-sm table-striped')
        if not table:
            continue
        headers = [th.get_text(strip=True) for th in table.thead.find_all('th')]
        if not headers:
            continue
        cat_name = headers[0]
        rows = []
        for tr in table.tbody.find_all('tr'):
            cols = [td.get_text(strip=True) for td in tr.find_all('td')]
            rows.append(cols)
        df = pd.DataFrame(rows, columns=headers)
        categories[cat_name] = df
    return categories


def save_to_excel(name: str, categories: dict):
    """Writes each category DataFrame to its own sheet in an Excel file."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, f"{name}.xlsx")
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        for cat, df in categories.items():
            sheet = cat[:31]
            df.to_excel(writer, sheet_name=sheet, index=False)
    logging.info(f"Wrote {len(categories)} sheets for {name} to {filepath}")


def main():
    pm = ProxyManager()
    muns = fetch_municipalities()
    for name, href in muns:
        # normalize to the actual data page URL
        if href.startswith('http'):
            raw_url = href
        else:
            raw_url = f"https://allecijfers.nl{href}"
        # overview pages use '/gemeente-overzicht/'; swap to '/gemeente/' for detailed data
        url = raw_url.replace('/gemeente-overzicht/', '/gemeente/')

        html = get_municipality_page(url, pm)
        if not html:
            continue
        cats = parse_tables(html)
        if cats:
            save_to_excel(name, cats)


if __name__ == '__main__':
    main()