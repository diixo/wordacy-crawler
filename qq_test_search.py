
import qq_grammar as qq
import json

class SearchTest:

    def __init__(self):
    
        self.unigrams = set()
        self.bigrams = set()
        self.trigrams = set()

    def add_tokens(self, tokens: list):
        sz = len(tokens)
        if sz == 1:
            ngrams_1 = qq.ngrams(tokens, 1)
            self.unigrams.update(ngrams_1)

        if sz == 2:
            ngrams_2 = qq.ngrams(tokens, 2)
            self.bigrams.update(ngrams_2)

        if sz == 3:
            ngrams_3 = qq.ngrams(tokens, 3)
            self.trigrams.update(ngrams_3)

    def set_keywords(self):
        stopwords = set()

        with open('./storage/allainews-news.json', 'r', encoding='utf-8') as fd:
            content = json.load(fd)
            keywords = content.get("keywords", list())
            ##########################################################################

            for string in keywords:
                grams = qq.str_tokenize_words(string)
                self.add_tokens(grams)
        
        ##########################################################################
        print(f"uni={len(self.unigrams)}, bi={len(self.bigrams)}, tri={len(self.trigrams)}")

def main():
    keywords = ["data science", "neural networks", "ai news"]
    test = SearchTest()
    test.set_keywords()

if __name__ == '__main__':
    main()
    
