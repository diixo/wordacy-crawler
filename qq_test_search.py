
import qq_grammar as qq

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

    def set_keywords(self, keywords = list()):
        stopwords = set()

        for string in keywords:
            string = qq.translate(string)
            ngrams = qq.str_to_ngrams(string, stopwords)
            for gram in ngrams:
                self.add_tokens(gram)
        return None

def main():
    keywords = ["data science", "neural networks", "ai news"]
    test = SearchTest()
    test.set_keywords(keywords=keywords)

if __name__ == '__main__':
    main()
    
