
import json
from pathlib import Path
import qq_parser as qq

class Analyzer:

   def __init__(self):

      self.urls = set()
      self.content = dict()

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

   def learn(self, url: str):
      url = url.lower().strip('/')
      if url in self.urls:
         print(f"url={url} already")
      else:
         qq.parse_url(url, self.content)
         self.urls.add(url)

   def learn_file(self, filename: str):
      path = Path(filename)
      if path.name in self.urls:
         print(f"file={path.name} already")
      else:
         if path.exists():
            qq.parse_file(filename, self.content)
            self.urls.add(path.name)

   def save_json(self, filename="_data.json"):
      rel = "./storage/"

      qq.save_json(self.content, rel + filename)

      filename="_urls.json"
      with open(rel + filename, 'w', encoding='utf-8') as fd:
         json.dump(sorted(self.urls), fd, ensure_ascii=False, indent=3)


   def analyse(self, url: str):
      pass

if __name__ == "__main__":
   u1 = "https://pythonexamples.org/"
   u2 = "https://kotlinandroid.org/"
   u3 = "https://www.javatpoint.com/"
   u4 = "http://neevo.net/"
   #u5 = "https://www.geeksforgeeks.org/generative-adversarial-network-gan/"
   #u5 = "https://javascriptcode.org/"
   #u5 = "https://www.javatpoint.com/python-variables"
   #u5 = "https://www.programiz.com/r"

   analyzer = Analyzer()
   #analyzer.learn_file('./process/techopedia-train-db-v5.data')
   analyzer.load_storage()
   analyzer.learn_file('./template/template.html')
   analyzer.learn(u1)
   analyzer.learn(u2)
   analyzer.learn(u3)
   analyzer.learn(u4)
   analyzer.save_json("_data.json")

