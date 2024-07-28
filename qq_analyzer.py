import time
import json
from pathlib import Path
import qq_parser as qq_parser
from qq_crawler2 import Crawler2
import qq_grammar as qq
from qq_prediction import Prediction



class ReversePaginator:
   def __init__(self, data, page_size):
      self.data = data
      self.page_size = page_size

   def get_page(self, page_index):
      result = []
      sz = len(self.data)

      start_index = max(sz - page_index * self.page_size, 0)
      end_index = sz - (page_index-1) * self.page_size
      #   if start_index < sz:
      #       end_index = min(page_index*self.page_size, sz)
      result = self.data[end_index - 1: start_index - 1 if start_index != 0 else None: -1]
      return result

   def num_pages(self):
      return (len(self.data) + self.page_size - 1) // self.page_size



def load_stopwords():
    f = Path("data/stopwords.txt")
    if f.exists():
        return set([line.replace('\n', '') for line in open(str(f), 'r', encoding='utf-8').readlines()])
    return set()

class Analyzer:

   def __init__(self):

      self.content = dict()
      self.content["urls"] = dict()
      self.urls = self.content["urls"]
      self.filepath = ""

   def open_json(self, filepath: str):
      path = Path(filepath)
      if path.exists():
         fd = open(filepath, 'r', encoding='utf-8')
         self.content = json.load(fd)
      self.filepath = filepath

      if not self.content.get("urls"):
         self.content["urls"] = dict()
      self.urls = self.content["urls"]


   def save_json(self, filepath = None):
      if filepath != None:
         self.filepath = filepath
      with open(self.filepath, 'w', encoding='utf-8') as fd:
         json.dump(self.content, fd, ensure_ascii=False, indent=3)


   def learn_url(self, url: str, hhh_mask = None):
      url = url.lower().strip('/')
      if url in self.urls:
         return False
      else:
         qq_parser.parse_url(url, self.content, hhh_mask=hhh_mask)
         self.urls[url] = ""
         return True

   def learn_file(self, filepath: str):
      path = Path(filepath)
      if path.name in self.urls:
         print(f"[Analyzer] file={path.name} done already")
      else:
         if path.exists():
            qq_parser.parse_file(filepath, self.content)
            self.urls[path.name] = ""

   def import_json(self, filepath: str):
      if not self.content.get("urls"):
         self.content["urls"] = dict()
      self.urls = self.content["urls"]

      hhh = self.content.get("headings", dict())
      self.content["headings"] = dict.fromkeys(hhh, "")

      path = Path(filepath)
      if path.exists():
         fd = open(filepath, 'r', encoding='utf-8')
         self.content = json.load(fd)
      self.filepath = filepath


def test_with_ssl():
   analyzer = Analyzer()
   analyzer.open_json("storage/ssl-content.json")
   analyzer.learn_url("https://www.linkedin.com/pulse/exploring-linear-regression-gradient-descent-mean-squared-ravi-singh", ["h1"])
   #analyzer.learn_url("https://www.marktechpost.com/2023/10/22/google-ai-presents-pali-3-a-smaller-faster-and-stronger-vision-language-model-vlm-that-compares-favorably-to-similar-models-that-are-10x-larger")
   analyzer.save_json()


