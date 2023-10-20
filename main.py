import os
import io
import re

from qq_analyzer import Analyzer
from qq_prediction import Prediction


def main():
    analyzer = Analyzer()
    analyzer.open_json("storage/allainews-news.json")
    result = analyzer.content.get("data", dict())
    print(len(result.keys()))


if __name__ == "__main__":
    main()
