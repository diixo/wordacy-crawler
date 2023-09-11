import os
import io
import urllib.parse
import json

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
#url = "https://www.datasciencecentral.com/category/technical-topics/data-science/"

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
        if title:
            print("<" + item.name + "> : " + title)
            train_db.write("<" + item.name + ">\n")
            train_db.write(": " + title)
            train_db.write("\n</" + item.name + ">\n")
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
def parse_url(url, train_db):
    req = Request(url, headers={'User-Agent': 'XYZ/3.0'})
    html = urllib.request.urlopen(req).read()
    raw = BeautifulSoup(html, features="html.parser")

    parse_structure(raw, train_db)


def parse_text(text: str):
    raw = BeautifulSoup(text, features="html.parser")
    parse_structure(raw, None)


def parseURL(url, train_db):
    req = Request(url, headers={'User-Agent': 'XYZ/3.0'})
    html = urllib.request.urlopen(req).read()
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
########################################################################

def read_li(raw, sz: int):
    li = raw.find_all("li")
    for item in li:
        span = item.find("span")
        if span:
            t = span.get_text().strip()
            if t: print("--"*sz + ">>" + t)
        a = item.find("a")
        if a:
            t = a.get_text().strip()
            if t: print("--"*sz + ">>" + t)

    #i.extract
    print("<<<<")

def parse_structure(raw, train_db):
    blacklist = [
        "head", "script", "style", "footer", "noscript", "iframe", "svg", "button", "img", "pre", "code"
    ]

    # kill all root-nodes in DOM-model: script and style elements
    for node in raw(blacklist):
        node.extract()  # cut it out

    cntr = 0

    while True:
        ul = raw.find("ul")
        if not ul: break

        while ul:
            ull = ul.find("ul")
            if not ull:
                read_li(ul, 1)
                ul.extract()
                break

            while ull:

                uus = ull.find("ul")
                if not uus:
                    read_li(ull, 2)
                    ull.extract()
                    break #break internal

                while uus:

                    uu = uus.find("ul")
                    if not uu:
                        read_li(uus, 3)
                        uus.extract()
                        break #break internal
                    
                    while uu:

                        u = uu.find("ul")
                        if not u:
                            read_li(uu, 4)
                            uu.extract()
                            break
                        else:
                            read_li(uu, 4)
                            #force stop deep iteration
                            uu.extract()
                            break                            

            print("  <</ul-1")
        ul.extract()


def parse(raw, train_db):
    blacklist = [
        "head", "script", "style", "footer", "noscript", "iframe", "svg", "button", "img", "pre", "code"
    ]

    header = raw.find_all("head")
    #proceed header-section separetely
    train_db.write("<head>\n")
    for h in header:

        htitle = h.find_all("title")
        for ht in htitle:
            writeElement(ht, train_db)

        ha = h.find_all("a")
        for a in ha:
            writeElement(a, train_db)
            a.extract()

        hli = h.find_all("li")
        for li in hli:
            writeElement(li, train_db)
    train_db.write("</head>\n")
    train_db.flush()

    # kill all root-nodes in DOM-model: script and style elements
    for node in raw(blacklist):
        node.extract()  # cut it out

    h1 = False

    train_db.write("<body>\n")

    for item in raw(["h1", "h2", "h3", "h4", "p", "a", "li"]):
        if item.name == 'h1':
            h1 = True
        if h1 == True:
            txt = item.get_text()
        else:
            txt = item.get_text()

        if hasattr(item, 'attrs'):
            if 'title' in item.attrs:
                writeTitleElement(item, item.attrs['title'], train_db)
            else: writeElement(item, train_db)
        else: writeElement(item, train_db)

    train_db.write("</body>\n")
    train_db.flush()
########################################################################
def parseFile(filename, train_db):
    raw = BeautifulSoup(open(filename, encoding='utf-8'), "html.parser")
    parse(raw, train_db)
########################################################################
