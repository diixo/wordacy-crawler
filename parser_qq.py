import os
import io
import json
import re
import urllib.parse

from urllib.request import urlopen
from bs4 import BeautifulSoup

from urllib.parse import urlparse
from urllib.request import Request

########################################################################

logging = False

def sanitize(str_line: str) -> bool:
    return not re.search(r'http:|https:|www\.', str_line, re.IGNORECASE)

def extract_keywords(raw):
    result = set()
    elements = raw.find_all("meta", {"name":"keywords"})
    for el in elements:
        s = el.attrs.get("content", "")
        s = str.replace(s, ',', ';')
        result.update([w.strip().lower() for w in s.split(';')])
    return result

def extract_h12(raw):
    h12 = raw.find_all(['h1', 'h2', 'h3'])
    result = set()
    result.update([h.get_text().lower().strip() for h in h12])
    return result


def read_li(raw, sz: int):
    if logging: print(">>>>")
    result = {}

    li = raw.find_all("li")

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
        if sanitize(k):
            dest[k] = dest.get(k, 0) + v

def extract_structure(raw, result:dict):
    blacklist = [
        "script", "style", "footer", "noscript", "iframe", "svg", "button", "img", "pre", "code"
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
                    break

                while uus:
                    uu = uus.find("ul")
                    if not uu:
                        extend(result, read_li(uus, 3))
                        uus.extract()
                        break
                    
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
def parse(raw):
    structure = {}
    extract_structure(raw, structure)
    keywords = extract_keywords(raw)
    h12s = extract_h12(raw)

    result = {}
    result['keywords'] = sorted(keywords)
    result['data'] = structure
    result['h12'] = sorted(h12s)

    with open('storage/data.json', 'w', encoding='utf-8') as fd:
        json.dump(result, fd, ensure_ascii=False, indent=3)

def parse_url(url):
    req = Request(url, headers={'User-Agent': 'XYZ/3.0'})
    html = urllib.request.urlopen(req).read()
    raw = BeautifulSoup(html, features="html.parser")
    parse(raw)

def parse_file(filename):
    raw = BeautifulSoup(open(filename, encoding='utf-8'), "html.parser")
    parse(raw)

def parse_text(text: str):
    raw = BeautifulSoup(text, features="html.parser")
    parse(raw)
########################################################################

def main():
    #parse_file("data/GeeksforGeeks-cs.html")

    url = "https://pythonexamples.org/"
    parse_url(url)


if __name__ == "__main__":
    main()
