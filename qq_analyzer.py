import time
import json
from pathlib import Path
import qq_parser as qq
from qq_crawler2 import Crawler2

class Analyzer:

   def __init__(self):

      self.urls = dict()
      self.content = dict()
      self.filepath = ""

   def open_json(self, filepath: str):
      path = Path(filepath)
      if path.exists():
         fd = open(filepath, 'r', encoding='utf-8')
         self.content = json.load(fd)
      #self.content["urls"] = dict()
      self.urls = self.content.get("urls", dict())
      self.filepath = filepath

   def save_json(self):
      #d = self.content.get("headings", dict())
      #self.content["headings"] = dict.fromkeys(d, "")

      if self.filepath != "": 
         with open(self.filepath, 'w', encoding='utf-8') as fd:
            #self.content["urls"] = dict.fromkeys(self.urls, "")
            json.dump(self.content, fd, ensure_ascii=False, indent=3)         


   def load_storage(self):
      rel = "./storage/"

      path = Path(rel + "_data.json")
      if path.exists():
         fd = open(rel + path.name, 'r', encoding='utf-8')
         self.content = json.load(fd)

      path = Path(rel + "_urls.json")
      if path.exists():
         fd = open(rel + path.name, 'r', encoding='utf-8')
         self.urls = set(json.load(fd))

   def learn(self, url: str, hhh_mask = None):
      url = url.lower().strip('/')
      if url in self.urls:
         #print(f"url={url} already")
         return False
      else:
         qq.parse_url(url, self.content, hhh_mask=hhh_mask)
         self.urls[url] = ""
         return True

   def learn_file(self, filepath: str):
      path = Path(filepath)
      if path.name in self.urls:
         print(f"file={path.name} already")
      else:
         if path.exists():
            qq.parse_file(filepath, self.content)
            self.urls.add(path.name)

   def save_storage(self, filename="_data.json"):
      rel = "./storage/"

      qq.save_json(self.content, rel + filename)

      filename="_urls.json"
      with open(rel + filename, 'w', encoding='utf-8') as fd:
         json.dump(sorted(self.urls), fd, ensure_ascii=False, indent=3)


   def analyse(self, url: str):
      pass


def test():
   url = "https://allainews.com/news/"

   crawler = Crawler2()
   crawler.enqueue_url(url)
   crawler.set_filter(url, [
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

   urls = crawler.get_urls(url)
   print(f"urls={len(urls)}")
   #for u in urls:
   #   print(u)

   analyzer = Analyzer()
   analyzer.open_json("storage/allainews-news.json")
   analyzer.learn(url, ["h1", "H1"])
   for u in urls:
      if analyzer.learn(u, ["h1", "H1"]):
         print(f"[Analyzer] ...on: {u}")
         time.sleep(2.0)
   analyzer.save_json()


if __name__ == "__main__":
   u1 = "https://pythonexamples.org/"
   u2 = "https://kotlinandroid.org/"
   u3 = "https://www.javatpoint.com/"
   u4 = "http://neevo.net/"
   #u5 = "https://www.geeksforgeeks.org/generative-adversarial-network-gan/"
   #u5 = "https://javascriptcode.org/"
   #u5 = "https://www.javatpoint.com/python-variables"
   #u5 = "https://www.programiz.com/r"

   test()
   exit(0)
   
   analyzer = Analyzer()
   #analyzer.learn_file('process/techopedia-train-db-v5.data')
   analyzer.load_storage()
   analyzer.learn_file('template/template.html')
   analyzer.learn(u1)
   analyzer.learn(u2)
   analyzer.learn(u3)
   analyzer.learn(u4)
   analyzer.save_storage()

