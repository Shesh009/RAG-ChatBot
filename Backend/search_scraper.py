import urllib.parse
import requests
from bs4 import BeautifulSoup

class SearchScraper:
    def search(self, query, max_results=5):
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
        return links

    def scrape(self, urls):
        contents = []
        for url in urls:
            try:
                html = requests.get(url, timeout=5).text
                soup = BeautifulSoup(html, "html.parser")
                headers = " ".join(h.get_text() for h in soup.find_all(['h1', 'h2', 'h3']))
                body = " ".join(p.get_text() for p in soup.find_all('p'))
                contents.append(f"{headers}\n{body}")
            except Exception as e:
                print(f"[ERROR] Failed scraping {url}: {e}")
        return "\n\n".join(contents)[:100000]
