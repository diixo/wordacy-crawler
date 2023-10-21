import os
import io
import re
import json
import string
from pathlib import Path

from qq_analyzer import Analyzer
from qq_prediction import Prediction


def load_dictionaries():
    stopwords = set()
    diix = Path("data/stopwords.txt")
    if diix.exists():
        stopwords = sorted([line.replace('\n', '') for line in open(str(diix), 'r', encoding='utf-8').readlines()])
        return set(stopwords)
    return stopwords

def split_to_ngrams(str_line: str):

    line1 = str_line.replace(". ", "! ")
    line1 = re.sub('[!?;,:\[\]\(\)]', "!", line1)
    strips = [x.strip() for x in line1.split("!") if x !='']

    punctuation = " ©®-%$!?:,;\'\" @~&()=*_<=>{|}[/]^\\"
    result = []

    for i, item in enumerate(strips):

        #words_list = [x.strip(" ") for x in item.split(" ") if (x != '')]
        #words_list = [x.strip(punctuation) if x not in self.dictionary else x for x in item.split(" ") if (x != '')]

        words_list = [x.strip(punctuation) for x in item.split(" ") if (x.strip(punctuation) != '')]

        result.append(words_list)
    return result


def main():
    stopwords = load_dictionaries()

    analyzer = Analyzer()
    analyzer.open_json("storage/allainews-news.json")
    
    content = analyzer.content.get("data", dict())

    prediction = Prediction()
    for string in content.keys():
        string = string.lower()
        ngrams = split_to_ngrams(string)
        for tokens in ngrams:
            prediction.add_tokens(tokens)

    result = {
        1:sorted(prediction.unigrams), 
        2:sorted(prediction.bigrams), 
        3:sorted(prediction.trigrams)
    }

    print(f"uni:{len(result[1])}, bi:{len(result[2])}, tri:{len(result[3])}")

    file_path="storage/_prediction.json"
    with open(file_path, 'w', encoding='utf-8') as fd:
        json.dump(result, fd, ensure_ascii=False, indent=3)


#s = "John's mom went there, but he wasn't c++, c#, .net, Q&A/Q-A, #nope i_t at-all'. So' she said: 'Where are& viix.co. !!' 'A a'"
#result = split_to_ngrams(s)

if __name__ == "__main__":
    main()
