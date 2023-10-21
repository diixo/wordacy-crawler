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

########################################################################

logging = False

stopwords = set()

def is_digit(word: str):
    w = re.sub(r'[$]?[-+]?[\d]*[.,\:]?[\d]+[ %\"\'\)\+]*', "", word)
    return not w

def is_complex_digit(word: str):
    w = re.sub(r'[$]?[-+]?[\d]*[.,\:]?[\d]+[ %\"\'\)\+]*[A-Za-z0-9]?', "", word)
    return not w

def str_tokenize_words(s: str):
    s = re.findall("(\.?\w[\w'\.&-]*\w|\w\+*#?)", s)
    if s: return s
    return []

def is_word(word: str, stopwords=set()):
    #word = re.search("[\[\]\}\{=@\*]")
    if (re.sub("[A-Za-z0-9#\'\./_&+-]", "", word) == "") and len(word) > 1:
        if ((word not in stopwords) and not word.isdigit() and not is_complex_digit(word)):
            return True
    return False


def sanitize(str_line: str) -> bool:
    return not re.search(r'http:|https:|www\.', str_line, re.IGNORECASE)

def translate(txt: str):
    translation = {
        0xfffd: 0x0020, 0x00b7: 0x0020, 0xfeff: 0x0020, 0x2026: 0x0020, 0x2713: 0x0020, 0x205F: 0x0020, 0x202c: 0x0020, 
        0x202a: 0x0020, 0x200e: 0x0020, 0x200d: 0x0020, 0x200c: 0x0020, 0x200b: 0x0020, 0x2002: 0x0020, 0x2003: 0x0020, 
        0x2009: 0x0020, 0x2011: 0x002d, 0x2015: 0x002d, 0x201e: 0x0020, 0x2028: 0x0020, 0x2032: 0x0027, 0x2012: 0x002d, 
        0x0080: 0x0020, 0x0094: 0x0020, 0x009c: 0x0020, 0xFE0F: 0x0020, 0x200a: 0x0020, 0x202f: 0x0020, 0x2033: 0x0020, 
        0x2013: 0x0020, 0x00a0: 0x0020, 0x2705: 0x0020, 0x2714: 0x0020, # 0x2013: 0x002d
        0x201c: 0x0020, 0x201d: 0x0020, 0x021f: 0x0020, 0x0022: 0x0020, 0x2019: 0x0027, 0x2018: 0x0027, 0x201b: 0x0027, 
        0x0060: 0x0027, 0x00ab: 0x0020, 0x00bb: 0x0020, 0x2026: 0x002e, 0x2014: 0x0020 } # 0x2014: 0x002d

    txt = txt.translate(translation)
    return txt.strip()

def set_text(txt: str):
    return translate(txt).lower()


def extract_keywords(raw, result = set()):

    elements = raw.find_all("meta", {"name":"keywords"})
    for el in elements:
        s = el.attrs.get("content", "")
        s = str.replace(s, ',', ';').split(';')
        result.update([set_text(w) for w in s if (w == "IT") or (not is_digit(w) and (w.lower() not in stopwords))])
    elements = raw.find_all("meta", {"name":"Keywords"})
    for el in elements:
        s = el.attrs.get("content", "")
        s = str.replace(s, ',', ';').split(';')
        result.update([set_text(w) for w in s if (w == "IT") or (not is_digit(w) and (w.lower() not in stopwords))])
    elements = raw.find_all("meta", {"name":"KEYWORDS"})
    for el in elements:
        s = el.attrs.get("content", "")
        s = str.replace(s, ',', ';').split(';')
        result.update([set_text(w) for w in s if (w == "IT") or (not is_digit(w) and (w.lower() not in stopwords))])
    
    tgs = raw.find_all('tag')
    result.update([set_text(t.get_text()) for t in tgs])
    if logging: print(f"<<<< tags:{len(tgs)}")

def extract_headings(raw, hhh_mask, result = set()):
    hhh = raw.find_all(hhh_mask)
    for h in hhh:
        s = str_tokenize_words(translate(h.get_text()))
        s = ' '.join([w.lower() for w in s if (w == "IT") or (not is_digit(w) and (w.lower() not in stopwords))])
        result.add(s)

def read_ahref(raw, structure=dict()):
    all = raw.find_all("a", {"class":"d-block text-dark"})
    for a in all:
        #s = str_tokenize_words(translate(a.get_text()))
        #s = ' '.join([w.lower() for w in s if (w == "IT") or (not is_digit(w) and (w.lower() not in stopwords))])
        # save original text:
        s = str.strip(translate(a.get_text()))
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

    structure = result.get('data', dict())
    keywords = set(result.get('keywords', []))
    hhh = set(result.get('headings', []))

    extract_keywords(raw, keywords)
    extract_headings(raw, hhh_mask, hhh)

    li_raw = read_li(raw, 1)
    hhh.update(li_raw.keys())

    #extract_structure(raw, structure)
    read_ahref(raw, structure)

    result['keywords'] = sorted(keywords)
    result['data'] = structure
    result['headings'] = sorted(hhh)

def parse_url(url, result = dict(), hhh_mask = None):
    req = Request(url, headers={'User-Agent': 'XYZ/3.0'})
    html = urllib.request.urlopen(req).read()
    if hhh_mask:
        raw = BeautifulSoup(html, features="html.parser", hhh_mask=hhh_mask)
    else:
        raw = BeautifulSoup(html, features="html.parser") 
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
