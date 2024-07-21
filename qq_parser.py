import os
import io
import json
import re
import ssl
from pathlib import Path
import urllib.parse

from urllib.request import urlopen
from bs4 import BeautifulSoup

from urllib.parse import urlparse
from urllib.request import Request

import qq_grammar as qq

########################################################################

logging = False
SSL_CONTEXT=ssl._create_unverified_context()
stopwords = set()


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

    if len(hhh) == 0:
        elements = raw.find_all("meta", {"property":"og:title"})
        for elem in elements:
            s = elem.attrs.get("content", None)
            if s:
                result[qq.translate(s)] = ""


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
def parse(raw, result = {}, div = None, hhh_mask = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
    hhh = dict()
    structure = result.get('data', dict())
    keywords = set(result.get('keywords', []))
    hhh = result.get('headings', dict())

    if div:
        result = list()
        texts_div = raw.find_all("div", { "class" : div })
        print(len(texts_div))
        result = [{
                    "title": text.get_text(), 
                    "abstract": text.get_text(),
                    "terms": ""
                } 
                for text in texts_div ]
        print(len(result))
    else:
        extract_keywords(raw, keywords)
        extract_headings(raw, hhh_mask, hhh)

        li_raw = read_li(raw, 1)
        #hhh.update(li_raw.keys())

        #extract_structure(raw, structure)
        #read_ahref(raw, structure)

        result['keywords'] = sorted(keywords)
        result['data'] = structure
        result['headings'] = hhh
    return result

def parse_url(url, result = dict(), div = None, hhh_mask = None):
    req = Request(url, headers={'User-Agent': 'XYZ/3.0'})
    #html = urllib.request.urlopen(req).read()
    html = urllib.request.urlopen(req, context = SSL_CONTEXT).read()
    raw = BeautifulSoup(html, features="html.parser") 
    if hhh_mask:
        result = parse(raw, result, div=div, hhh_mask=hhh_mask)
    else:
        result = parse(raw, result, div=div)
    return result

def parse_file(filename, result = dict(), div = None, hhh_mask = None):
    raw = BeautifulSoup(open(filename, encoding='utf-8'), "html.parser")
    if hhh_mask:
        result = parse(raw, result, div, hhh_mask=hhh_mask)
    else:
        result = parse(raw, result, div)
    return result

def save_json(result: dict, file_path="storage/_data.json"):
    with open(file_path, 'w', encoding='utf-8') as fd:
        json.dump(result, fd, ensure_ascii=False, indent=3)

########################################################################

categories = {
    #"cs.SE": ["app", "application"],
    "cs.MM": ["video", "videos", "animation", "music", "animations", "subtitling"],
    "cs.GR": ["image", "images", "photo", "photos", "3d", "renders", "rendering", "texture", "textures", "gui", "midjourney", "cg", 
              "art", "designs", "design", "2d"],
    "cs.AI": ["chatgpt", "ai", "ai-powered", "huggingface", "ai-generated", "ai-driven", "ai-enhanced", "ai-prompted", "midjourney", 
              "neural", "autogpt", "gpt-3", "ai-based"],
    "cs.CY": ["chatgpt",],                              # Computers and Society
    "cs.HI": ["chatgpt", "chat", "ui"],                 # Human-Computer Interfaces
    "cs.SI": ["aggregate", "aggregates", "social", "platform", "platforms"],     # Social and Information Networks
    "cs.LG": ["llm", "llms", "huggingface", "ml", "neural", "training"],            # Machine learning
    "cs.CL": ["llm", "llms", "transcription", "translation",],    # Computation and Language
    "cs.HC": ["llm", "llms", "ux"],                     # Human-Computer Interaction
    "cs.IR": ["summarize", "summarization", "extraction", "emails", "documents", "extracts", "summaries", "retrieval",
              "patterns"],  
                                                        # information retrieval
    "cs.NI": ["cloud",],                                # Networking and Internet Architecture
    #"cs.OS": [ "ios", "macos" ],
    "cs.SD": ["sound", "voice", "audio", "music", "speech", "voiceovers", "voiceover", "audios", "voice-to-text", 
              "audio-to-text", "speech-to-text"],
    "cs.CV": ["upscaler", "face", "facial"],
    "cs.PL": ["programming", "sdk", "development"],
    "cs.DB": [],
}

categories_txt = {
    "cs.CV": ["augmented reality", "computer vision"],
    "cs.LG": ["language model", "machine learning", "data science"],
    "cs.HC": ["data visuali"],
    "cs.PL": ["deploy"],
    "cs.DB": ["database",],
    "cs.CL": ["natural language", "language processing"],
    "cs.IR": ["natural language", "language processing"]
}


def arxiv_json_classify(dataset: list):
    for item in dataset:
        item["terms"] = "cs.SE"

        text = item["abstract"].lower()
        words = qq.str_tokenize_words(text)
        for term, keywords in categories.items():
            keywords = set(keywords)
            for word in words:
                if word in keywords:
                    item["terms"] = item["terms"] + " " + term
                    break
            phrases = categories_txt.get(term, None)
            if phrases:
                for ph in phrases:
                    if text.find(ph) >= 0:
                        item["terms"] = item["terms"] + " " + term
                        break



def main():
    result = parse_file("c:/futuretools.html", div="tool-item-description-box---new")
    #result = parse_file('process/techopedia-train-db-v5.data')

    #url = "https://pythonexamples.org/"
    #url = "https://GeeksforGeeks.org/"
    #result = parse_url(url)

    #arxiv_json_classify(result)

    save_json(result, file_path="storage/futuretools.json")


if __name__ == "__main__":
    # rel = "./data/"

    # path = Path(rel + "stopwords.txt")
    # if path.exists():
    #     stopwords.update([line.replace('\n', '')
    #     for line in open(rel + path.name, 'r', encoding='utf-8').readlines()])

    main()
