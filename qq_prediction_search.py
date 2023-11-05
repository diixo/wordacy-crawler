import json

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
            value = tpl[id-1]
            t = tuple(tpl[0:id-1])
            if len(t) == 1: t = tpl[0]
            else: continue

            #print(f"{t} : {value}")
            dct_freq = dct.get(t, { value : 0 })

            fr = dct_freq[value] if (value in dct_freq) else 0
            dct_freq[value] = fr + 1

            dct[t] = dct_freq


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
