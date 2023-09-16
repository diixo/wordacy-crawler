
import json
from pathlib import Path
import parser_qq as qq

class Manager:

   def __init__(self):

      self.urls = set()
      self.content = dict()

   def load_storage(self):
      rel = "./storage/"

      path = Path(rel + "data.json")
      if path.exists():
         fd = open(rel + path.name, 'r', encoding='utf-8')
         self.content = json.load(fd)

      path = Path(rel + "urls.json")
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

   def save_json(self):
      rel = "./storage/"

      filename="data.json"
      qq.save_json(self.content, rel + filename)

      filename="urls.json"
      with open(rel + filename, 'w', encoding='utf-8') as fd:
         json.dump(sorted(self.urls), fd, ensure_ascii=False, indent=3)


   def analyse(self, url: str):
      pass

if __name__ == "__main__":
   u1 = "https://pythonexamples.org/"
   u2 = "https://kotlinandroid.org/"
   u3 = "https://www.javatpoint.com/"
   u4 = "http://neevo.net/"

   manager = Manager()
   manager.load_storage()
   manager.learn_file('./data/technologies-ibm.html')
   manager.learn(u1)
   manager.learn(u2)
   manager.learn(u3)
   manager.learn(u4)
   manager.save_json()

