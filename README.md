## html-crawler

### Crawler
Crawler - search and collect all finding URL's from specified source web-page. Save generated urls list into json-format

### Tokenizer
Tokenizer - split sentences on separated words

### Analizer
Analizer - analyze input page by content of DOM-elements like keywords, lists, p-tags, a-tags, span-tags, h1-h6 headers.

### Examples:
Parameter **recursive**=False crawl only links from specified urls.

Parameter **recursive**=True crawl with traversing recursively (all links from each domain).

```python
   crawler = Crawler2(recursive=False)
   crawler.open_json("urls.json")

   crawler.enqueue_url("https://name-1.com/sub/page", ["/privacy-policy"])
   crawler.enqueue_url("https://name-2.com/sub/page", ["/terms-of-use"])
   crawler.enqueue_url("https://name-3.com/sub/page", ["/donation"])

   crawler.run()

   # save "urls.json"
   crawler.save_json()
```
Format of output json-file as urls-list:
```json
{
   "https://domain-name.com": [
      "https://domain-name.com/url_1/",
      "https://domain-name.com/url_2/"
   ]
}
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
Save logical storage, as pair of two files: **storage/_data.json** and **storage/_urls.json**
```python
   analyzer.save_storage()
```
Format of output json-file (**storage/_data.json**):
```json
{
   "keywords": [],
   "data": {},
   "headings": []
}
```
