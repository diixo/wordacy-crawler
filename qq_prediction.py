import re
from operator import itemgetter
from collections import Counter
from pathlib import Path
import qq_grammar as qq

########################################################################
# nltk.ngrams
def ngrams(content, n):
   ngramList = [tuple(content[i:i+n]) for i in range(len(content)-n+1)]
   return ngramList
########################################################################
def add_ngrams_freqDict(ngram_freq_dict, ngramList):
   for tpl in ngramList:
      if tpl in ngram_freq_dict:
            ngram_freq_dict[tpl] += 1
      else:
            ngram_freq_dict[tpl] = 1
##########################################################
def str_tokenize(str_line: str, stopwords = None):
   word_list = qq.str_tokenize_words(str_line)
   if word_list:
      if stopwords:
         return [w for w in word_list if w not in stopwords]
      else:
         return word_list
   return []

########################################################################
def predict_next_word_smoothed(last_word, probDist):
   next_word = {}
   for k in probDist:
      if k[0] == last_word[0]:
         next_word[k[1]] = probDist[k]
   k = Counter(next_word)
   high = k.most_common(1) 
   return high[0]
########################################################################
def predict_next_3_words_smoothed(token, probDist):
   pred1 = []
   pred2 = []
   next_word = {}
   for i in probDist:
      if i[0] == token:
         next_word[i[1]] = probDist[i]
   k = Counter(next_word)
   high = k.most_common(2) 
   w1a = high[0]
   w1b = high[1]
   w2a = predict_next_word_smoothed(w1a, probDist)
   w3a = predict_next_word_smoothed(w2a, probDist)
   w2b = predict_next_word_smoothed(w1b, probDist)
   w3b = predict_next_word_smoothed(w2b, probDist)
   pred1.append(w1a)
   pred1.append(w2a)
   pred1.append(w3a)
   pred2.append(w1b)
   pred2.append(w2b)
   pred2.append(w3b)
   return pred1, pred2
########################################################################
def predict_next_word(last_word, probDist):
   next_word = {}
   for k in probDist:
      if k[0:2] == last_word:
         next_word[k[2]] = probDist[k]
   k = Counter(next_word)
   high = k.most_common(1) 
   return high[0]
########################################################################
def predict_next_3_words(token, probDist):
   pred = []
   next_word = {}
   for i in probDist:
      if list(i[0:2]) == token:
         next_word[i[2]] = probDist[i]
   k = Counter(next_word)
   high = k.most_common(10)
   if len(high) > 0:
      w1a = high[0]
      print("<< high:", [ item[0] for item in high ])
      tup = (token[1], w1a[0])
      w2a = predict_next_word(tup, probDist)
      tup = (w1a[0], w2a[0])
      w3a = predict_next_word(tup, probDist)
      pred.append(w1a)
      pred.append(w2a)
      pred.append(w3a)
   return pred
########################################################################

class Prediction:
   
   def __init__(self):
      self.unigrams = set()
      self.bigrams = set()
      self.trigrams = set()
      self.unigrams_freq_dict = {}  # freq_dict for unigrams
      self.bigrams_freq_dict  = {}  # freq_dict for bigrams
      self.trigrams_freq_dict = {}  # freq_dict for trigrams

   def __str__(self) -> str:
      return f"Prediction: [#1:{len(self.unigrams_freq_dict)}, #2:{len(self.bigrams_freq_dict)}, #3:{len(self.trigrams_freq_dict)}]"

   ##########################################################

   def predict_next(self, str_line: str):
      tokenList = str_tokenize(str_line)
      sz = len(tokenList)

      bigrams_probDist = {}
      V = len(self.bigrams)

      for i in self.bigrams_freq_dict:
         bigrams_probDist[i] = (self.bigrams_freq_dict[i] + 1) / (self.unigrams_freq_dict[tuple([i[0]])] + V)

      trigrams_probDist = {}
      for i in self.trigrams_freq_dict:
         trigrams_probDist[i] = (self.trigrams_freq_dict[i] + 1) / (self.bigrams_freq_dict[i[0:2]] + V)

      if (sz == 1):
         token = tokenList[0]
         pred1, pred2 = predict_next_3_words_smoothed(token, bigrams_probDist)
         return (str_line, [[item1[0] for item1 in pred1], [item2[0] for item2 in pred2]])

      if (sz == 2):
         pair = [tokenList[0], tokenList[1]]
         pred_3 = predict_next_3_words(pair, trigrams_probDist)
         return (str_line, [item[0] for item in pred_3])
      return []
   ##########################################################
   def size(self):
      return len(self.unigrams)

   def add_word(self, word: str):
      ngrams_1 = ngrams([word], 1)
      add_ngrams_freqDict(self.unigrams_freq_dict, ngrams_1)
      self.unigrams.update(ngrams_1)  # unique inserting

   def add_tokens(self, tokens: list):
      ngrams_1 = ngrams(tokens, 1)
      ngrams_2 = ngrams(tokens, 2)
      ngrams_3 = ngrams(tokens, 3)

      add_ngrams_freqDict(self.unigrams_freq_dict, ngrams_1)
      add_ngrams_freqDict(self.bigrams_freq_dict,  ngrams_2)
      add_ngrams_freqDict(self.trigrams_freq_dict, ngrams_3)

      self.unigrams.update(ngrams_1)  # unique inserting
      self.bigrams.update(ngrams_2)   # unique inserting
      self.trigrams.update(ngrams_3)  # unique inserting

   def finalize(self, dictionary = set()):
      if self.size() == 0: return

      str_path = "./__prediction/"
      with Path(str_path) as path:
         if not path.exists(): path.mkdir()

      self.unigrams = sorted(self.unigrams)
      self.bigrams  = sorted(self.bigrams)
      self.trigrams = sorted(self.trigrams)

      f = open(str_path + "unigrams-new-sort.utf8", 'w', encoding='utf-8')
      counter1 = 0
      counter_n = 0
      counter_1 = 0
      for w in self.unigrams:
         v = self.unigrams_freq_dict[w]
         if w[0] not in dictionary:
            f.write(f"{w[0]} ; {v}\n")
            counter_n += 1
            counter_1 += v
         counter1 += v
      f.close()

      f = open(str_path + "bigrams-sort.utf8", 'w', encoding='utf-8')
      counter2 = 0
      for ws in self.bigrams:
         v = self.bigrams_freq_dict[ws]
         f.write(f"{ws[0]}; {ws[1]}; {str(v)}" + "\n")
         counter2 += v
      f.close()

      print(">> unigrams, bigrams, trigrams: sz={}({}), sz={}({}), sz={}".format(
         len(self.unigrams), counter1, len(self.bigrams), counter2, len(self.trigrams)))

      print(f"<< unigrams, candidates new.sz={counter_n}({counter_1})")
##########################################################

   def get_sorted(self):
      result = {
         1:sorted(self.unigrams_freq_dict.items(), key=itemgetter(1), reverse=True),
         2:sorted(self.bigrams_freq_dict.items(),  key=itemgetter(1), reverse=True),        
         3:sorted(self.trigrams_freq_dict.items(), key=itemgetter(1), reverse=True)
      }
      return result

   def get_dicts(self):
      result = {
        1:sorted(self.unigrams), 
        2:sorted(self.bigrams), 
        3:sorted(self.trigrams)
      }
      return result

##########################################################
   def predict(str_line: str, stopwords = set()):
      work_str = qq.translate(str_line, stopwords)
      tokenList = str_tokenize(work_str)

      ngram = {1:[], 2:[]}

      for i in range(2):
         ngram[i+1] = list(ngrams(tokenList, i+1))[-1]
##########################################################