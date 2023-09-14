
import json
from pathlib import Path

class Manager:

   def __init__(self):

      self.urls = set()
      self.content = dict()

   def load(self):
      rel = "./data/"

      path = Path(rel + "urls.txt")
      if path.exists():
         self.urls.update([line.replace('\n', '')
            for line in open(rel + path.name, 'r', encoding='utf-8').readlines()])

      path = Path("./storage/data.json")
      if path.exists():
         fd = open("./storage/data.json", 'r', encoding='utf-8')
         self.content = json.load(fd)

if __name__ == "__main__":
   manager = Manager()
   manager.load()

