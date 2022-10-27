import urllib.parse

from urllib.request import urlopen
from bs4 import BeautifulSoup

from urllib.parse import urlparse
from urllib.request import Request

url = "https://www.datasciencecentral.com/top-10-projects-for-data-science-and-machine-learning/"
#url = "https://www.techopedia.com/definition/26184/c-plus-plus-programming-language"

req = Request(url, headers={'User-Agent': 'XYZ/3.0'})
html = urllib.request.urlopen(req).read()
raw = BeautifulSoup(html, features="html.parser")

# kill all root-nodes in DOM-model: script and style elements
for node in raw(["script", "style", "header", "footer", "noscript", "iframe", "svg", "button", "img", "span"]):
    node.extract()   # cut it out

# get text
text = raw.get_text()

def parse(soup):
    h1 = False
    for item in soup(["h1", "h2", "h3", "h4", "p", "a"]):
        if item.name == 'h1':
            h1 = True
        if h1 == True:
            print(item.get_text())

parse(raw)

# break into lines and remove leading and trailing space on each
lines = (line.strip() for line in text.splitlines())

# break multi-headlines into a line each
chunks = (phrase.strip() for line in lines for phrase in line.split("  "))

# drop blank lines
text = '\n'.join(chunk for chunk in chunks if chunk)

print(text)
