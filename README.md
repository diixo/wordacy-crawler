# html-crawler

### Crawler
Crawler - search and collect all finding URL's from specified source web-page. Save generated urls list into json-format

### Tokenizer
Tokenizer - split sentences on separated words

### Analizer
Analizer - analyze input page by content of DOM-elements like keywords, lists, p-tags, a-tags, span-tags, h1-h6 headers.

### Params:
Parameter **Crawler2**(**recursive**=False): crawl only links from specified urls.

Parameter **Crawler2**(**recursive**=True): crawl with traversing recursively (all links from each domain).

## Examples:
### 1) Crawl web-page:
```python
   crawler = Crawler2(recursive=False)
   crawler.open_json("urls.json")

   crawler.enqueue_url("https://name-1.com/sub/page")
   crawler.enqueue_url("https://name-2.com/sub/page")
   crawler.enqueue_url("https://name-3.com/sub/page")

   crawler.set_filter("https://name-1.com", ["/privacy-policy"])
   crawler.set_filter("https://name-2.com", ["/privacy-policy"])
   crawler.set_filter("https://name-3.com", ["/privacy-policy"])

   crawler.run()

   # save "urls.json"
   crawler.save_json()
```
### 2) Crawl local html-file:
Extract all links of specified domain from local file:
```python
   crawler = Crawler2()
   crawler.extract_from_file("filename.html", "https://domain.com/", ["/privacy-policy"])

   # save output-file as ./storage/domain.com.json
   crawler.save_json()
```
**Crawler2** output json-file as urls-list:
```json
{
   "https://name.com": [
      "https://name.com/url_1/",
      "https://name.com/url_2/"
   ]
}
```
### 3) Smart analysis the content from url's:

```python
   analyzer = Analyzer()
   analyzer.open_json("some.json")
   analyzer.learn_file("template/template.html")
   analyzer.learn_url(url_1)
   analyzer.learn_url(url_2)
   analyzer.learn_url(url_3)
   analyzer.save_json()
```

Format of output json-file:
```json
{
   "keywords": [],
   "data": {},
   "headings": []
}
```
