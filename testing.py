import requests
import html
from bs4 import BeautifulSoup

url = 'https://coincodex.com/historical-data/crypto/?date=2022-07-25T04:00:00Z'

r = requests.get(url)
soup = BeautifulSoup(r.text, 'lxml')
print(soup.prettify)