import os
import io
import re
import uuid

import parserqq as qq


def main():
    url = "https://www.geeksforgeeks.org"
    #qq.parse_url(url, None)
    qq.parse_file("data/GeeksforGeeks-cs.html")
    exit(0)

    name =  re.sub("https://", "", url) + f"_{uuid.uuid4().hex}.txt"
    name = "data/" + name

    train_db = open(name, 'w', encoding='utf-8')

    # clean raw text
    #qq.parse_url(url, train_db)
    #qq.list_dir("./html", train_db)

    train_db.close()
    print("<<")


if __name__ == "__main__":
    main()
