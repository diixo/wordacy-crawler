import json
from pathlib import Path

# graph should be construct from keywords-section of json dataset
# should provide fast searching by unigram, bigram
# based on searching tree

def tgrams(content, n):
   ngramList = [tuple(content[i:i+n]) for i in range(len(content)-n+1)]
   return ngramList

class PredictionSearch:

   def __init__(self):
      self.graph = dict()
      self.graph['1'] = dict()
      self.graph['2'] = dict()
      self.graph['3'] = dict()

   def add_ngrams_freq(self, id:int, ngramList):
      dct = self.graph[str(id)]
      if (id == 1):
         for tpl in ngramList:
            if tpl[0] in dct:
               dct[tpl[0]] += 1
            else:
               dct[tpl[0]] = 1
      else:
         for tpl in ngramList:
            key = " ".join(tpl[0:id-1])
            value = tpl[id-1]

            #print(f"{key} : {value}")
            dct_freq = dct.get(key, { value : 0 })

            fr = dct_freq[value] if (value in dct_freq) else 0
            dct_freq[value] = fr + 1

            dct[key] = dct_freq


   def add_tokens(self, tokens: list):
      ngrams_1 = tgrams(tokens, 1)
      ngrams_2 = tgrams(tokens, 2)
      ngrams_3 = tgrams(tokens, 3)

      self.add_ngrams_freq(1, ngrams_1)
      self.add_ngrams_freq(2, ngrams_2)
      self.add_ngrams_freq(3, ngrams_3)

   def save_json(self, filepath = None):
      if filepath:
         with open(filepath, 'w', encoding='utf-8') as fd:
            json.dump(self.graph, fd, ensure_ascii=False, indent=3)

   def load_json(self, filepath: str):
      path = Path(filepath)
      if path.exists():
         fd = open(filepath, 'r', encoding='utf-8')
         self.graph = json.load(fd)

   def search(self, grams_list: list):
      sz = len(grams_list)
      if sz >= len(self.graph): return []

      d = self.graph[str(sz+1)]
      items = d.get(" ".join(grams_list), dict())

      result = dict()
      for k, v in items.items():
         vector = result.get(v, None)
         if vector:
            vector.append(k)
         else:
            result[v] = [k]

      srt = sorted(result.items(), reverse=True)
      #srt=list(tuple(cntr, [...]))

      result = []
      cntr = 0
      for tpl in srt:
         if len(result) + len(tpl[1]) <= 50:
            result.extend(tpl[1])
            cntr += 1
         else: break
      print(f"results: [{cntr}:{len(srt)}]")
      return result