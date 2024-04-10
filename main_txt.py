
import qq_grammar as qq
from qq_prediction_search import load_words


if __name__ == "__main__":
    
    vocabulary = load_words("data/db-full.txt")

    fd = open("make-dataset/train.devices.txt", 'r', encoding='utf-8')

    result = dict()
        
    while True:
        line = fd.readline()
        if not line:
            break;

        words = qq.str_tokenize_words(line.lower())
        filtered = [w for w in words if w not in vocabulary]

        print(len(words), ":", len(filtered))

        for w in filtered:
            freq = result[w] if (w in result) else 0
            result[w] = freq + 1

    print("vocabulary:", len(vocabulary))
    print("<<<", len(result))
