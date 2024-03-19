
import json
import time
from pathlib import Path

from qq_analyzer import Analyzer

analyzer = Analyzer()
analyzer.open_json("dataset.json")

def load_urls():
    f = Path("urls.txt")
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

