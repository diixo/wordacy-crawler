import os
import io
import re
import json
import string
from pathlib import Path

from qq_analyzer import Analyzer
from qq_prediction import Prediction
import qq_parser as qq


def load_stopwords():
    diix = Path("data/stopwords.txt")
    if diix.exists():
        return set([line.replace('\n', '') for line in open(str(diix), 'r', encoding='utf-8').readlines()])
    return set()


def str_to_ngrams(str_line: str, stopwords: set()):

    line1 = str_line.replace(". ", "! ")
    line1 = re.sub('[!?;,:\[\]\(\)]', "!", line1)
    strips = [x.strip() for x in line1.split("!") if x !='']

    punctuation = " ©®-%$!?:,;\'\" @~&()=*_<=>{|}[/]^\\"
    result = []
    exclude = { "2d", "3d", "3g", "4g", "5g", "6g" }

    for item in strips:

        #words_list = [x.strip(" ") for x in item.split(" ") if (x != '')]
        #words_list = [x.strip(punctuation) if x not in self.dictionary else x for x in item.split(" ") if (x != '')]

        word_list = [x.strip(punctuation) for x in item.split(" ") if (x.strip(punctuation) != '')]
        tokens = []
        for w in word_list:
            wlow = w.lower()
            if (w == "IT") or (wlow == "c#") or (wlow in exclude):
                tokens.append(wlow)
            else:
                wlow = wlow.strip("#")
                if qq.is_word(wlow, stopwords):
                    tokens.append(wlow)

        if tokens: result.append(tokens)
    return result


def test_prediction():
    stopwords = load_stopwords()

    analyzer = Analyzer()
    #open constant version:
    analyzer.open_json("storage/_prediction-allainews-news.json")
    
    content = analyzer.content.get("data", dict())

    prediction = Prediction()
    for string in content.keys():
        string = qq.translate(string)
        ngrams = str_to_ngrams(string, stopwords)
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


if __name__ == "__main__":
    test_prediction()
