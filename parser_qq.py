import os
import io
import json
import urllib.parse

from urllib.request import urlopen
from bs4 import BeautifulSoup

from urllib.parse import urlparse
from urllib.request import Request

########################################################################

logging = False

def read_li(raw, sz: int):
    if logging: print(">>>>")
    result = {}

    li = raw.find_all("li")

    #print(raw.name)
    #if raw.attrs and raw.attrs.get('class'):
    #    print(raw.attrs.get('class'))

    for item in li:
        if item.find("ul"):
            span = item.find("span")
            if span:
                t = span.get_text().strip()
                if t:
                    if logging: print("--" * sz + ">>##" + t)
                    t = t.lower()
                    result[t] = result.get(t, 0) + 1
                    continue
            a = item.find("a")
            if a:
                t = a.get_text().strip()
                if t:
                    if logging: print("--" * sz + ">>##" + t)
                    t = t.lower()
                    result[t] = result.get(t, 0) + 1
                    continue
            #break
        else:
            span = item.find("span")
            if span:
                t = span.get_text().strip()
                if t:
                    t = t.lower()
                    result[t] = result.get(t, 0) + 1
                    if logging: print("--" * sz + ">>" + t)
            a = item.find("a")
            if a:
                t = a.get_text().strip()
                if t:
                    t = t.lower()
                    result[t] = result.get(t, 0) + 1
                    if logging: print("--" * sz + ">>" + t)
    #i.extract
    if logging: print("<<<<")
    return result

def extend(dest:dict(), src:dict()):
    for k, v in src.items():
        dest[k] = dest.get(k, 0) + v

def parse_structure(raw, result:dict):
    blacklist = [
        "head", "script", "style", "footer", "noscript", "iframe", "svg", "button", "img", "pre", "code"
    ]

    # kill all root-nodes in DOM-model: script and style elements
    for node in raw(blacklist):
        node.extract()  # cut it out

    while True:
        ul = raw.find("ul")
        if not ul: break
        else: extend(result, read_li(ul, 1))

        while ul:
            ull = ul.find("ul")
            if not ull:
                extend(result, read_li(ul, 1))
                ul.extract()
                break

            while ull:
                uus = ull.find("ul")
                if not uus:
                    extend(result, read_li(ull, 2))
                    ull.extract()
                    break #break internal

                while uus:
                    uu = uus.find("ul")
                    if not uu:
                        extend(result, read_li(uus, 3))
                        uus.extract()
                        break #break internal
                    
                    while uu:
                        u = uu.find("ul")
                        if not u:
                            extend(result, read_li(uu, 4))
                            uu.extract()
                            break
                        else:
                            extend(result, read_li(uu, 4))
                            #force stop deep iteration
                            uu.extract()
                            break                            
        ul.extract()
########################################################################
def parse_url(url, train_db):
    req = Request(url, headers={'User-Agent': 'XYZ/3.0'})
    html = urllib.request.urlopen(req).read()
    raw = BeautifulSoup(html, features="html.parser")

    result = {}
    parse_structure(raw, result)
    with open('storage/data.json', 'w', encoding='utf-8') as fd:
        json.dump(result, fd, ensure_ascii=False, indent=2)

def parse_file(filename):
    raw = BeautifulSoup(open(filename, encoding='utf-8'), "html.parser")
    result = {}
    parse_structure(raw, result)
    print(result)

def parse_text(text: str):
    raw = BeautifulSoup(text, features="html.parser")
    result = {}
    parse_structure(raw, result)
    print(result)
########################################################################

def main():
    #parse_file("data/GeeksforGeeks-cs.html")

    url = "https://pythonexamples.org/"
    parse_url(url, None)


if __name__ == "__main__":
    main()
