
import qq_grammar as qq
import json

class SearchTest:

    def __init__(self):
    
        self.unigrams = set()
        self.bigrams = set()
        self.trigrams = set()

        with open('./storage/allainews-news.json', 'r', encoding='utf-8') as fd:
            content = json.load(fd)
            keywords = content.get("keywords", list())
            ##########################################################################

            for string in keywords:
                grams = qq.str_tokenize_words(string)
                self.add_tokens(grams)
        
        ##########################################################################
        print(f"uni={len(self.unigrams)}, bi={len(self.bigrams)}, tri={len(self.trigrams)}")

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


    def calculate_tags(self, heading, stopwords=set()):
        grams = qq.str_tokenize_words(heading.lower())
        result = []
        #for tokens in grams:
        ngrams_1 = qq.ngrams(grams, 1)
        result.extend([" ".join(gram) for gram in ngrams_1 if gram in self.unigrams])
        
        ngrams_2 = qq.ngrams(grams, 2)
        result.extend([" ".join(gram) for gram in ngrams_2 if gram in self.bigrams])
        
        ngrams_3 = qq.ngrams(grams, 3)
        result.extend([" ".join(gram) for gram in ngrams_3 if gram in self.trigrams])
        # TODO: unique results
        return result

def main():
    test = SearchTest()

    result = test.calculate_tags("Large Language model: Java News Roundup: Spring Shell, Micronaut, JReleaser, JobRunr", 
        set())
    print(result)

if __name__ == '__main__':
    main()
    
