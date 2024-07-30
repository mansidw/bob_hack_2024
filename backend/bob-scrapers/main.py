import requests
from bs4 import BeautifulSoup


url = "https://www.bankofbaroda.in/personal-banking/accounts/saving-accounts"
reqs = requests.get(url)
soup = BeautifulSoup(reqs.text, "html.parser")
print(soup)
urls = []
for link in soup.find_all("a"):
    print(link.get("href"))
