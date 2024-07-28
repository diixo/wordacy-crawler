
from qq_parser import parse_file, arxiv_json_classify, save_json


def main():
    result = parse_file("c:/futuretools.html", div="tool-item-description-box---new")
    #result = parse_file('process/techopedia-train-db-v5.data')

    #url = "https://pythonexamples.org/"
    #url = "https://GeeksforGeeks.org/"
    #result = parse_url(url)

    arxiv_json_classify(result)

    save_json(result, file_path="storage/futuretools.json")


if __name__ == "__main__":
    # rel = "./data/"

    # path = Path(rel + "stopwords.txt")
    # if path.exists():
    #     stopwords.update([line.replace('\n', '')
    #     for line in open(rel + path.name, 'r', encoding='utf-8').readlines()])

    main()

