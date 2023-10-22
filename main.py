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
    diix = Path("data/stopwords.txt")
    if diix.exists():
        return set([line.replace('\n', '') for line in open(str(diix), 'r', encoding='utf-8').readlines()])
    return set()


def test_prediction():
    stopwords = load_stopwords()

    analyzer = Analyzer()
    #open constant version:
    analyzer.open_json("storage/_prediction-allainews-news.json")
    
    content = analyzer.content.get("keywords", dict())
    content = dict.fromkeys(content, "")

    prediction = Prediction()
    for string in content.keys():
        string = qq_grammar.translate(string)
        ngrams = qq_grammar.str_to_ngrams(string, stopwords)
        for tokens in ngrams:
            prediction.add_tokens(tokens)

    result = prediction.get_dicts()

    print(prediction)

    file_path="storage/_prediction.json"
    with open(file_path, 'w', encoding='utf-8') as fd:
        json.dump(result, fd, ensure_ascii=False, indent=3)

    if False:
        file_path="storage/_prediction-sorted.json"
        with open(file_path, 'w', encoding='utf-8') as fd:
            json.dump(prediction.get_sorted(), fd, ensure_ascii=False, indent=3)

    tpl = prediction.predict_next("ai")
    print(tpl)

    tpl = prediction.predict_next("software")
    print(tpl)


if __name__ == "__main__":
    test_prediction()
