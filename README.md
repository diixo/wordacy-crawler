## html-crawler

### Crawler
Crawler - search and collect all finding URL's from specified source web-page. Possibility to save collection into json-format

### Tokenizer
Tokenizer - split sentences on separated words

### Analizer
Analizer - analyze pages with collect content of DOM-elements like keywords, lists, p-tags, a-tags, span-tags, h1-h6 headers.

### Examples:
```python
   crawler = Crawler()
   techopedia = crawler.open_json("some.json")
   crawler.run("https://kotlinandroid.org/")
   crawler.run("https://javascriptcode.org/")

   # crawl with filter
   crawler.run("https://devopedia.org", ["/search/", "/user/"])

   #save opened json
   crawler.save_json()
```

```python
   analyzer = Analyzer()
   analyzer.open_json("some.json")
   analyzer.learn("https://allainews.com/news/")

   #save opened json
   analyzer.save_json()
```

```python
   analyzer = Analyzer()
   analyzer.load_storage()
   analyzer.learn_file('template/template.html')
   analyzer.learn(url_1)
   analyzer.learn(url_2)
   analyzer.learn(url_3)
   analyzer.save_storage()
```
