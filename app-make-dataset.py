
import json
import time
from pathlib import Path

from qq_analyzer import Analyzer
import qq_grammar as qq


f = Path("data/db-full.txt")
diixonary = set()
if f.exists():
    diixonary = set([line.replace('\n', '') for line in open(str(f), 'r', encoding='utf-8').readlines()])
print(len(diixonary))

f = Path("make-dataset/train.devices.txt")
if f.exists():
    for line in open(str(f), 'r', encoding='utf-8').readlines():
        words = qq.str_tokenize_words(line.lower())
        result = [w for w in words if (w not in diixonary and not qq.is_digit(w))]
        print(result)

print(result)
exit(0)

analyzer = Analyzer()
analyzer.open_json("make-dataset/dataset.json")

def load_urls():
    f = Path("make-dataset/urls.txt")
    if f.exists():
        return [line.replace('\n', '') for line in open(str(f), 'r', encoding='utf-8').readlines()]
    return []

urls = load_urls()

print(f">> [Analyzer] :{len(analyzer.content.get('headings', dict()))}")
for u in urls:
    if analyzer.learn_url(u, hhh_mask=["h1", "H1"]):
        print(f"[Analyzer] ...on [{len(urls)}]: {u}")
        time.sleep(2.0)
analyzer.save_json()
print(f"<< [Analyzer] :{len(analyzer.content.get('headings', dict()))}")

