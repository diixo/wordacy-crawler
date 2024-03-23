
import json
import time
from pathlib import Path


import qq_grammar as qq
from qq_analyzer import Analyzer
from qq_crawler2 import Crawler2


def process_file():
    f = Path("data/db-full.txt")
    diixonary = set()
    if f.exists():
        diixonary = set([line.replace('\n', '') for line in open(str(f), 'r', encoding='utf-8').readlines()])
    print(len(diixonary))

    f = Path("make-dataset/dataset.txt")
    if f.exists():
        for line in open(str(f), 'r', encoding='utf-8').readlines():
            line = qq.translate(line.lower())
            words = qq.str_tokenize_words(line)
            result = [w for w in words if (w not in diixonary and not qq.is_digit(w))]
            print(result)

    print(result)


def test_url_to_dataset():
    url = "https://www.simplilearn.com"

    crawler = Crawler2(recursive=True)
    crawler.enqueue_url(url)
    crawler.set_filter(url, [
      "/about-us",
      "/careers",
      "/contact-us",
      "/feed",
      "/guest-blogging",
      "/terms-and-conditions",

      "/terms/", 
      "/privacy/", 
      "/accounts/", 
      "/filtered/", 
      "/videos/", 
      "/feed/", 
      "/topic/",
      "/source/",
      "/news/feed",
      "/term",
      "/about",
      "/podcasts",
      "/sources.md"
      ])
    crawler.run()
    crawler.save_json("test/simplilearn.com.json")

if __name__ == "__main__":
    #exit(0)
    test_url_to_dataset()
