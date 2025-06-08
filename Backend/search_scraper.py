import logging
import urllib.parse
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class SearchScraper:
    def search(self, query, max_results=5):
        logger.info(f"Searching DuckDuckGo for: {query}")
        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        links = []
        for a in soup.find_all('a', class_='result__a', href=True):
            raw_url = a['href']
            parsed = urllib.parse.urlparse(raw_url)
            actual_url = urllib.parse.parse_qs(parsed.query).get('uddg', [None])[0]
            if actual_url and not any(site in actual_url for site in ['youtube', 'twitter', 'facebook']):
                links.append(actual_url)
            if len(links) >= max_results:
                break
        logger.info(f"Found {len(links)} URLs")
        return links

    def scrape(self, urls):
        logger.info(f"Scraping content from {len(urls)} URLs")
        contents = []
        for url in urls:
            try:
                html = requests.get(url, timeout=5).text
                soup = BeautifulSoup(html, "html.parser")
                headers = " ".join(h.get_text() for h in soup.find_all(['h1', 'h2', 'h3']))
                body = " ".join(p.get_text() for p in soup.find_all('p'))
                contents.append(f"{headers}\n{body}")
            except Exception as e:
                logger.exception(f"Failed scraping {url}")
        return "\n\n".join(contents)[:100000]
