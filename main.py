import os
import io
import re
import json
import string
from pathlib import Path

from qq_analyzer import Analyzer
from qq_prediction import Prediction
import qq_grammar as qq_grammar


def load_stopwords():
    f = Path("data/stopwords.txt")
    if f.exists():
        return set([line.replace('\n', '') for line in open(str(f), 'r', encoding='utf-8').readlines()])
    return set()


def test_prediction():
    stopwords = load_stopwords()

    analyzer = Analyzer()
    #open constant version:
    analyzer.open_json("storage/_prediction-allainews-news.json")

    #open dynamic version:
    #analyzer.open_json("storage/allainews-news.json")
    
    content = analyzer.content.get("headings", dict())
    content = dict.fromkeys(content, "")

    prediction = Prediction()
    for string in content.keys():
        string = qq_grammar.translate(string)
        ngrams = qq_grammar.str_to_ngrams(string, stopwords)
        for tokens in ngrams:
            prediction.add_tokens(tokens)


    print(prediction)

    if True:
        file_path="storage/_prediction-freq.json"
        prediction.save_json(file_path)

        ccc = 36
        amount = 50
        tpl = prediction.predict_next("ai")
        print(tpl)

        tpl = prediction.predict_next("software")
        print(tpl)

        print(prediction.get_1("ai"))
        print(prediction.get_2("software", "engineering"))

        result_freq = prediction.get_freq_sorted()

        print(ccc*"-")
        for i in range(amount):
            print(f"{result_freq['1'][i][0]}: {result_freq['1'][i][1]}")
        print(ccc*"-")

        for i in range(amount):
            print(f"{result_freq['2'][i][0]}: {result_freq['2'][i][1]}")
        print(ccc*"-")

        prediction.load_json(file_path)
        prediction.save_json(file_path)


if __name__ == "__main__":
    test_prediction()
