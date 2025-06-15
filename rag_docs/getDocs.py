from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

def get_all_docs_links(base_url):
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, "html.parser")
    links = []

    for link_tag in soup.findAll('a', href=True):
        href=link_tag['href']

        if '/youtube/' in href:
            full_url = urljoin(base_url, href)
            links.append(full_url)

    return list(set(links))


all_links = get_all_docs_links("https://docs.chaicode.com/youtube/getting-started/")

# print("Found Urls: ")
# print(all_links)
# for link in all_links:
#     print(link)