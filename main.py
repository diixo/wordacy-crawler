import os
import io
import re
import json
import string
from pathlib import Path

from qq_analyzer import Analyzer
from qq_prediction import Prediction
import qq_parser as qq


def load_dictionaries():
    stopwords = set()
    diix = Path("data/stopwords.txt")
    if diix.exists():
        stopwords = sorted([line.replace('\n', '') for line in open(str(diix), 'r', encoding='utf-8').readlines()])
        return set(stopwords)
    return stopwords


def split_to_ngrams(str_line: str, stopwords: set()):

    line1 = str_line.replace(". ", "! ")
    line1 = re.sub('[!?;,:\[\]\(\)]', "!", line1)
    strips = [x.strip() for x in line1.split("!") if x !='']

    punctuation = " ©®-%$!?:,;\'\" @~&()=*_<=>{|}[/]^\\"
    result = []

    for item in strips:

        #words_list = [x.strip(" ") for x in item.split(" ") if (x != '')]
        #words_list = [x.strip(punctuation) if x not in self.dictionary else x for x in item.split(" ") if (x != '')]

        word_list = [x.strip(punctuation) for x in item.split(" ") if (x.strip(punctuation) != '')]
        tokens = []
        for w in word_list:
            wlow = w.lower()
            if (w == "IT") or qq.is_word(wlow, stopwords):
                tokens.append(wlow)

        result.append(tokens)
    return result


def test_prediction():
    stopwords = load_dictionaries()

    analyzer = Analyzer()
    #open constant version:
    analyzer.open_json("storage/_prediction-allainews-news.json")
    
    content = analyzer.content.get("data", dict())

    prediction = Prediction()
    for string in content.keys():
        string = qq.translate(string)
        ngrams = split_to_ngrams(string, stopwords)
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


#s = "John's mom went there, but he wasn't c++, c#, .net, Q&A/Q-A, #nope i_t at-all'. So' she said: 'Where are& viix.co. !!' 'A a'"
#result = split_to_ngrams(s)

if __name__ == "__main__":
    test_prediction()
