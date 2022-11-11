import os
import io
import urllib.parse

from urllib.request import urlopen
from bs4 import BeautifulSoup

from urllib.parse import urlparse
from urllib.request import Request

#url = "https://www.datasciencecentral.com/top-10-projects-for-data-science-and-machine-learning/"
#url = "https://www.techopedia.com/definition/26184/c-plus-plus-programming-language"
########################################################################
# https://understandingdata.com/python-for-seo/how-to-extract-text-from-multiple-webpages-in-python/
# https://stackoverflow.com/questions/328356/extracting-text-from-html-file-using-python

#url = "https://www.labri.fr/perso/nrougier/from-python-to-numpy/"
#url = "https://www.ibm.com/cloud/blog/supervised-vs-unsupervised-learning/"
url = "https://www.datasciencecentral.com/category/technical-topics/data-science/"

train_db = open("train-db.txt", 'w', encoding='utf-8')

########################################################################
def processString(str):
    txt = str.replace('\n', ' ')
    txt = txt.replace('\t', ' ')
    txt = txt.replace('\u00a0', ' ')
    txt = txt.strip()  # trim spaces
    return txt
########################################################################
def writeElement(item, train_db):
    txt = processString(item.get_text())
    if txt:
        print("<" + item.name + "> " + txt)
        train_db.write("<" + item.name + ">\n")
        train_db.write(txt)
        train_db.write("\n</" + item.name + ">\n")
########################################################################
def writeTitleElement(item, text, train_db):
    txt = processString(item.get_text())
    title = processString(text)
    if txt:
        print("<" + item.name + "> " + txt)
        train_db.write("<" + item.name + ">\n")
        train_db.write(txt + " : " + title)
        train_db.write("\n</" + item.name + ">\n")
    else:
        print("<" + item.name + "> :")
        train_db.write("<" + item.name + ">\n")
        train_db.write(": " + title)
        train_db.write("\n</" + item.name + ">\n")
########################################################################
def parseURL(url, train_db):
    req = Request(url, headers={'User-Agent': 'XYZ/3.0'})
    html = urllib.request.urlopen(req).read()
    raw = BeautifulSoup(html, features="html.parser")

    blacklist = [
        "header", "script", "style", "footer", "noscript", "iframe", "svg", "button", "img", "span", "pre",
    ]

    header = raw.find_all("header")
    #proceed header-section separetely
    train_db.write("<header>\n")
    for h in header:
        ha = h.find_all("a")
        for a in ha:
            writeElement(a, train_db)
            a.extract()

        hli = h.find_all("li")
        for li in hli:
            writeElement(li, train_db)
    train_db.write("</header>\n")

    # kill all root-nodes in DOM-model: script and style elements
    for node in raw(blacklist):
        node.extract()  # cut it out
    
    parse(raw, train_db)
    return

    # get text
    text = raw.get_text()

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())

    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))

    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)

    print(text)
########################################################################
def parse(soup, train_db):
    h1 = False
    txt = ""

    train_db.write("<body>\n")

    for item in soup(["h1", "h2", "h3", "h4", "p", "a", "li"]):
        if item.name == 'h1':
            h1 = True
        if h1 == True:
            txt = item.get_text()
        else:
            txt = item.get_text()

        txt = processString(txt)

        if (not txt): txt = "<" + item.name + ">"

        if hasattr(item, 'attrs'):
            if 'title' in item.attrs:
                writeTitleElement(item, item.attrs['title'], train_db)
            else: writeElement(item, train_db)
        else: writeElement(item, train_db)

    train_db.write("</body>\n")
########################################################################
def parseFile(filename, train_db):
    raw = BeautifulSoup(open(filename, encoding='utf-8'), "html.parser")
    parse(raw, train_db)
########################################################################
def list_dir(dir_path, train_db):
    i = 0
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if (file.endswith(".html")):
                print(os.path.join(root, file))
                parseFile(os.path.join(root, file), train_db)
                i += 1
                print(i)
########################################################################

# clean raw text
parseURL(url, train_db)

train_db.close()
