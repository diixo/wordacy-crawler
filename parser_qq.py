import os
import io
import urllib.parse

from urllib.request import urlopen
from bs4 import BeautifulSoup

from urllib.parse import urlparse
from urllib.request import Request

########################################################################

def read_li(raw, sz: int):
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
                    print("--" * sz + ">>##" + t)
                    continue
            a = item.find("a")
            if a:
                t = a.get_text().strip()
                if t:
                    print("--" * sz + ">>##" + t)
                    continue
            #break
        else:
            span = item.find("span")
            if span:
                t = span.get_text().strip()
                if t: print("--" * sz + ">>" + t)
            a = item.find("a")
            if a:
                t = a.get_text().strip()
                if t: print("--" * sz + ">>" + t)


    #i.extract
    print("<<<<")

def parse_structure(raw, file_db):
    blacklist = [
        "head", "script", "style", "footer", "noscript", "iframe", "svg", "button", "img", "pre", "code"
    ]

    # kill all root-nodes in DOM-model: script and style elements
    for node in raw(blacklist):
        node.extract()  # cut it out

    while True:
        ul = raw.find("ul")
        if not ul: break
        else: read_li(ul, 1)

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
########################################################################
def parse_url(url, train_db):
    req = Request(url, headers={'User-Agent': 'XYZ/3.0'})
    html = urllib.request.urlopen(req).read()
    raw = BeautifulSoup(html, features="html.parser")

    parse_structure(raw, train_db)

def parse_file(filename):
    raw = BeautifulSoup(open(filename, encoding='utf-8'), "html.parser")
    parse_structure(raw, None)

def parse_text(text: str):
    raw = BeautifulSoup(text, features="html.parser")
    parse_structure(raw, None)
########################################################################

def main():
    parse_file("data/GeeksforGeeks-cs.html")


if __name__ == "__main__":
    main()
