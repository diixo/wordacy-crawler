
from pathlib import Path

class Manager:

   def __init__(self):

      self.urls = set()

   def load_data(self):
      rel = "./data/"

      path = Path(rel + "urls.txt")
      if path.exists():
         self.urls.update([line.replace('\n', '')
            for line in open(rel + path.name, 'r', encoding='utf-8').readlines()])

