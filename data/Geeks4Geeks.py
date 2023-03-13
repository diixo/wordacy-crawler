import os
import io
import urllib.parse
import time

from urllib.request import urlopen
from bs4 import BeautifulSoup

from urllib.parse import urlparse
from urllib.request import Request

url = "https://www.datasciencecentral.com/top-10-projects-for-data-science-and-machine-learning/"
#url = "https://www.techopedia.com/definition/26184/c-plus-plus-programming-language"
########################################################################
# https://understandingdata.com/python-for-seo/how-to-extract-text-from-multiple-webpages-in-python/
# https://stackoverflow.com/questions/328356/extracting-text-from-html-file-using-python

#url = "https://www.labri.fr/perso/nrougier/from-python-to-numpy/"
#url = "https://www.ibm.com/cloud/blog/supervised-vs-unsupervised-learning/"
#url = "https://www.datasciencecentral.com/category/technical-topics/data-science/"

train_db = open("train-db-xml-geeks.data", 'w', encoding='utf-8')
train_f = open("train-db-files.txt", 'w', encoding='utf-8')

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
        #print("<" + item.name + "> " + txt)
        train_db.write("<" + item.name + ">\n")
        train_db.write(txt)
        train_db.write("\n</" + item.name + ">\n")

def writeElementText(item, train_db):
    txt = item.get_text().replace('\t', ' ')
    txt = txt.replace('\u00a0', ' ')
    txt = txt.strip()  # trim spaces
    if txt:
        # print("<" + item.name + "> " + txt)
        train_db.write("<" + item.name + ">\n")
        train_db.write(item.get_text())
        train_db.write("\n</" + item.name + ">\n")
########################################################################
def writeTitleElement(item, text, train_db):
    txt = processString(item.get_text())
    title = processString(text)
    if txt:
        #print("<" + item.name + "> " + txt)
        train_db.write("<" + item.name + ">\n")
        train_db.write(txt + " : " + title)
        train_db.write("\n</" + item.name + ">\n")
    else:
        if title:
            #print("<" + item.name + "> : " + title)
            train_db.write("<" + item.name + ">\n")
            train_db.write(": " + title)
            train_db.write("\n</" + item.name + ">\n")
########################################################################
def parseURL(url, train_db):
    req = Request(url, headers={'User-Agent': 'XYZ/3.0'})

    try:
        response = urllib.request.urlopen(req)
        html = response.read()
        raw = BeautifulSoup(html, features="html.parser")

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
    except urllib.error.URLError as e:
        if hasattr(e, 'code'):
            print(e.code)
        if hasattr(e, 'reason'):
            print(e.reason)
    except urllib.error.HTTPError as e:
        if hasattr(e, 'code'):
            print(e.code)
########################################################################
def parse(raw, train_db):
    blacklist = [
        "head", "script", "style", "footer", "noscript", "iframe", "svg", "button", "img", "pre", "code"
    ]

    #write raw-title if content absent
    titlehead = raw.find('header', attrs={'class': 'entry-header'})

    if not titlehead:
        titlehead = raw.find('div', attrs={'class': 'article-title'})

    if titlehead:
        train_db.write("<title>\n")
        for title in titlehead(["h1", "p"]):
            writeElement(title, train_db)
        train_db.write("</title>\n")
    #############################################################

    # kill all root-nodes in DOM-model: script and style elements
    for node in raw(blacklist):
        node.extract()  # cut it out

    content = raw.find('div', attrs={'class': 'page_content'})

    if not content:
        content = raw.find('div', attrs={'class': 'text'})

    if not content: return

    train_db.write("<body>\n")

    #write raw text of content ########
    #writeElementText(content, train_db)
    train_db.flush()

    for item in content(["h2", "h3", "h4", "p", "li"]):
        writeElement(item, train_db)

    tags = raw.find('div', attrs={'class': 'nv-tags-list'})
    if tags:
        train_db.write("<tags>\n")
        for tag in tags(["p", "a", "li"]):
            writeElement(tag, train_db)
        train_db.write("</tags>\n")

    train_db.write("</body>\n")
    train_db.flush()
    print("<<")
########################################################################
def parseFile(filename, train_db):
    raw = BeautifulSoup(open(filename, encoding='utf-8'), "html.parser")
    parse(raw, train_db)
########################################################################
def list_dir(dir_path, train_db):
    i = 0
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if (file.endswith(".htm")):
                print(os.path.join(root, file))
                train_f.write(os.path.join(root, file) + "\n")
                train_f.flush()
                parseFile(os.path.join(root, file), train_db)
                i += 1
                print(i)
########################################################################

file_urls = open('auditor_url_children.txt', 'r', encoding='utf-8')

count = 0
while True:

    line = file_urls.readline()

    if not line:
        break;

    count += 1
    if line.find('www.geeksforgeeks.org') > 0:
        train_f.write(line.strip() + "\n")
        train_f.flush()
        print(str(count) + ") " + line.strip())
        parseURL(line.strip(), train_db)
        time.sleep(1.0)

# clean raw text
#parseFile("D:/html/www.datasciencecentral.com-edited/debunking-the-myth-of-analytic-talent/index-1.htm", train_db)
#parseURL("https://www.datasciencecentral.com/dsc-webinar-series-scale-ai-ml-with-data-wrangling-featuring-forrester/", train_db)
#parseURL("https://www.datasciencecentral.com/6-limitations-of-desktop-system-that-quickbooks-hosting-helps/", train_db)
#parseFile("D:/html/www.datasciencecentral.com-edited/index-116.htm", train_db)
#parseURL("https://www.datasciencecentral.com/social-media-sentiment-analysis-using-twitter-datasets/", train_db)
#list_dir("D:/html", train_db)

train_f.close()
train_db.close()
