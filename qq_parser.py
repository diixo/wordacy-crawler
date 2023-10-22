import os
import io
import json
import re
from pathlib import Path
import urllib.parse

from urllib.request import urlopen
from bs4 import BeautifulSoup

from urllib.parse import urlparse
from urllib.request import Request

import qq_grammar as qq

########################################################################

logging = False

stopwords = set()


def is_word(word: str, stopwords=set()):
    #word = re.search("[\[\]\}\{=@\*]")
    if (re.sub("[A-Za-z0-9#\'\./_&+-]", "", word) == "") and len(word) > 1:
        if ((word not in stopwords) and not word.isdigit() and not qq.is_complex_digit(word)):
            return True
    return False


def sanitize(str_line: str) -> bool:
    return not re.search(r'http:|https:|www\.', str_line, re.IGNORECASE)


def set_text(txt: str):
    return qq.translate(txt).lower()


def extract_keywords(raw, result = set()):

    elements = raw.find_all("meta", {"name":"keywords"})
    for el in elements:
        s = el.attrs.get("content", "")
        s = str.replace(s, ',', ';').split(';')
        result.update([set_text(w) for w in s if (w == "IT") or (not qq.is_digit(w) and (w.lower() not in stopwords))])
    elements = raw.find_all("meta", {"name":"Keywords"})
    for el in elements:
        s = el.attrs.get("content", "")
        s = str.replace(s, ',', ';').split(';')
        result.update([set_text(w) for w in s if (w == "IT") or (not qq.is_digit(w) and (w.lower() not in stopwords))])
    elements = raw.find_all("meta", {"name":"KEYWORDS"})
    for el in elements:
        s = el.attrs.get("content", "")
        s = str.replace(s, ',', ';').split(';')
        result.update([set_text(w) for w in s if (w == "IT") or (not qq.is_digit(w) and (w.lower() not in stopwords))])
    
    tgs = raw.find_all('tag')
    result.update([set_text(t.get_text()) for t in tgs])
    if logging: print(f"<<<< tags:{len(tgs)}")

def extract_headings(raw, hhh_mask, result = dict()):
    hhh = raw.find_all(hhh_mask)
    for h in hhh:
        s = qq.translate(h.get_text())
        #s = "".join([w for w in s if (w == "IT") or (not qq.is_digit(w) and (w not in stopwords))])
        result[s] = ""

def read_ahref(raw, structure=dict()):
    all = raw.find_all("a")
    for a in all:
        #s = str_tokenize_words(qq.translate(a.get_text()))
        #s = ' '.join([w.lower() for w in s if (w == "IT") or (not qq.is_digit(w) and (w.lower() not in stopwords))])
        # save original text:
        s = str.strip(qq.translate(a.get_text()))
        if s: structure[s] = structure.get(s, 0) + 0

def read_li(raw, sz: int):
    if logging: print(">>>>")
    result = {}

    tags = ["ul", "ol"]
    li = raw.find_all("li")

    for item in li:
        if item.find(tags):
            span = item.find("span")
            if span:
                t = set_text(span.get_text())
                if t:
                    if logging: print("--" * sz + ">>##" + t)
                    result[t] = result.get(t, 0) + 1
                    continue
            a = item.find("a")
            if a:
                t = set_text(a.get_text())
                if t:
                    if logging: print("--" * sz + ">>##" + t)
                    result[t] = result.get(t, 0) + 1
                    continue
            #break
        else:
            span = item.find("span")
            if span:
                t = set_text(span.get_text())
                if t:
                    result[t] = result.get(t, 0) + 1
                    if logging: print("--" * sz + ">>" + t)
            a = item.find("a")
            if a:
                t = set_text(a.get_text())
                if t:
                    result[t] = result.get(t, 0) + 1
                    if logging: print("--" * sz + ">>" + t)
            ####
            if (not a) and (not span):
                t = set_text(item.get_text())
                if t:
                    if logging: print("--" * sz + ">>" + t)
                    result[t] = result.get(t, 0) + 1
    #i.extract
    if logging: print("<<<<")
    return result

def extend(dest:dict, src:dict):
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

    tags = ["ul", "ol"]

    while True:
        ul = raw.find(tags)
        if not ul: break
        else: extend(result, read_li(ul, 1))

        while ul:
            ull = ul.find(tags)
            if not ull:
                extend(result, read_li(ul, 1))
                ul.extract()
                break

            while ull:
                uus = ull.find(tags)
                if not uus:
                    extend(result, read_li(ull, 2))
                    ull.extract()
                    break

                while uus:
                    un = uus.find(tags)
                    if not un:
                        extend(result, read_li(uus, 3))
                        uus.extract()
                        break

                    while un:
                        uu = un.find(tags)
                        if not uu:
                            extend(result, read_li(un, 4))
                            un.extract()
                            break
                    
                        while uu:
                            u = uu.find(tags)
                            if not u:
                                extend(result, read_li(uu, 5))
                                uu.extract()
                                break
                            else:
                                extend(result, read_li(uu, 5))
                                #force stop deep iteration
                                uu.extract()
                                break
        ul.extract()
########################################################################
def parse(raw, result = {}, hhh_mask = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
    hhh = dict()
    structure = result.get('data', dict())
    keywords = set(result.get('keywords', []))
    hhh = result.get('headings', dict())

    extract_keywords(raw, keywords)
    extract_headings(raw, hhh_mask, hhh)

    li_raw = read_li(raw, 1)
    #hhh.update(li_raw.keys())

    #extract_structure(raw, structure)
    #read_ahref(raw, structure)

    result['keywords'] = sorted(keywords)
    result['data'] = structure
    result['headings'] = hhh

def parse_url(url, result = dict(), hhh_mask = None):
    req = Request(url, headers={'User-Agent': 'XYZ/3.0'})
    html = urllib.request.urlopen(req).read()
    raw = BeautifulSoup(html, features="html.parser") 
    if hhh_mask:
        parse(raw, result, hhh_mask=hhh_mask)
    else:
        parse(raw, result)
    return result

def parse_file(filename, result = dict()):
    raw = BeautifulSoup(open(filename, encoding='utf-8'), "html.parser")
    parse(raw, result)
    return result

def save_json(result: dict, file_path="storage/_data.json"):
    with open(file_path, 'w', encoding='utf-8') as fd:
        json.dump(result, fd, ensure_ascii=False, indent=3)

########################################################################

def main():
    result = parse_file("data/GeeksforGeeks-cs.html")
    #result = parse_file('process/techopedia-train-db-v5.data')

    #url = "https://pythonexamples.org/"
    #url = "https://GeeksforGeeks.org/"
    #result = parse_url(url)

    save_json(result)


if __name__ == "__main__":
    rel = "./data/"

    path = Path(rel + "stopwords.txt")
    if path.exists():
        stopwords.update([line.replace('\n', '')
        for line in open(rel + path.name, 'r', encoding='utf-8').readlines()])

    main()
