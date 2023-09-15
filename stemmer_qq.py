
import json
from pathlib import Path

def main():
    
    dictionary = dict()
    rel = "./data/"
    diix = Path(rel + "vocab-cyr.txt")
    sz = 5

    if diix.exists():
        fd = open(rel + diix.name, 'r', encoding='utf-8')
        
        for line in fd.readlines():
            line = line.strip()
            if len(line) < sz: continue

            string = line[0:sz]
            dictionary[string] = dictionary.get(string, 0) + 1

    result = {}
    value = 0
    for k, v in dictionary.items():
        if v >= 10:
            result[k] = v
            value += v

    with open('./storage/stemming.json', 'w', encoding='utf-8') as fo:
        json.dump(result, fo, ensure_ascii=False, indent=3)

    print(f"...on={value}.")

##########################
if __name__ == "__main__":
    main()
