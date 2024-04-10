
import json
import qq_grammar as qq
from qq_prediction_search import load_words


def translate(txt: str):
    translation = {
        0x2019: 0x0027, 0x00d7: 0x0020, 0x00ab: 0x0020, 0x00bb: 0x0020, }

    return txt.translate(translation)

if __name__ == "__main__":
    
    vocabulary = load_words("data/db-full.txt")

    fd = open("make-dataset/train.devices.txt", 'r', encoding='utf-8')

    result = dict()
        
    while True:
        line = fd.readline()
        if not line:
            break;

        words = qq.str_tokenize_words(translate(line.lower()))

        filtered = [w for w in words if w not in vocabulary and not qq.is_digit(w)]

        print(len(words), "filtered:", len(filtered), "unique:", len(set(filtered)))

        for w in filtered:
            result[w] = result.get(w, 0) + 1


    with open("tmp.json", 'w', encoding='utf-8') as fd:
        json.dump(result, fd, ensure_ascii=False, indent=3)

    print("vocabulary:", len(vocabulary))
    print("<<<", len(result))

    # with open("main_txt.json", 'w', encoding='utf-8') as fd:
    #     json.dump(result, fd, indent=3)
