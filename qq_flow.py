
import json
from pathlib import Path
import qq_parser as qq

class FlowAnalyzer:

   def __init__(self):

      self.urls = dict()
      self.content = dict()
      self.queue = list()

      self.content['keywords'] = set()
      self.content['data'] = set()
      self.content['headings'] = set()

   def __str__(self):
      s1 = f"loaded: queue={len(self.queue)}, domains=[{len(self.urls)}]\n"
      s2 = "\n".join([f"   [{k}] = {len(v)}" for k, v in self.urls.items()])
      return s1 + s2

   def queue_json(self, filepath:str):
      path = Path(filepath)
      if path.exists():
         fd = open(filepath, 'r', encoding='utf-8')
         result = json.load(fd)
         for v in result.values():
            self.queue.extend(v)
         self.urls.update(result)


   def load_json(self, filepath="storage/_flow.json"):
      path = Path(filepath)
      if path.exists():
         fd = open(filepath, 'r', encoding='utf-8')
         result = json.load(fd)
         self.urls = result
         self.queue = list()


   def save_json(self, filepath="storage/_flow.json"):
      with open(filepath, 'w', encoding='utf-8') as fd:
         json.dump(self.urls, fd, ensure_ascii=False, indent=3)


if __name__ == "__main__":
   flow = FlowAnalyzer()
   flow.queue_json("storage/www.futuretools.io.json")
   flow.queue_json("storage/aivalley.ai.json")
   flow.queue_json("storage/openfuture.ai.json")
   flow.queue_json("storage/allainews.com.json")
   flow.save_json("storage/_flow.json")
   flow = FlowAnalyzer()
   flow.queue_json("storage/_flow.json")
   print(flow)
   flow.load_json("storage/_flow.json")
   print(flow)
