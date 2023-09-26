
import json
from urllib.parse import urlparse
from usp.tree import sitemap_tree_for_homepage


def save_json(hostname:str, result:dict):
   filepath = "./storage/" + hostname + ".json"
   with open(filepath, 'w', encoding='utf-8') as fd:
      json.dump(result, fd, ensure_ascii=False, indent=3)

def make_sitemap(url, filter):

   url = str.strip(url, '/')

   filter = set([(url + f) for f in filter])
   tree = sitemap_tree_for_homepage(url)

   urls = set()

   for page in tree.all_pages():
      for f in filter:
         if (str.find(page.url, f) >= 0): break
      else: urls.add(page.url)   #without break

   print(f"sz={len(urls)}")
   result = dict()
   result[url] = sorted(urls)
   save_json(urlparse(url).hostname, result=result)


def main():

   make_sitemap("https://openfuture.ai", 
      ["/user", "/blog/", "/contact-us", "/privacy-policy", "/terms-conditions", "/about-us", "/ai-tools/"])

   return

   make_sitemap(
      "https://www.techopedia.com",
      ["/contributors/", "/companies/", "/contact", "/advertise", "/about/", "/subscribe"])


##########################
if __name__ == "__main__":
    main()
