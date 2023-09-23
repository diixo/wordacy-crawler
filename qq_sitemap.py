
import json
from urllib.parse import urlparse
from usp.tree import sitemap_tree_for_homepage


def save_json(hostname:str, result:dict):
   filepath = "./storage/" + hostname + ".json"
   with open(filepath, 'w', encoding='utf-8') as fd:
      json.dump(result, fd, ensure_ascii=False, indent=3)


def main():

   url = str.strip("https://www.techopedia.com", '/')
   filter = ["/contributors/", "/companies/", "/contact", "/advertise", "/about/", "/subscribe"]

   filter = set([(url + f) for f in filter])
   tree = sitemap_tree_for_homepage(url)

   urls = set()
   find = False

   for page in tree.all_pages():
      find = False
      for f in filter:
         if (str.find(page.url, f) >= 0):
            find = True
            break
      if not find: urls.add(page.url)
      

   print(f"sz={len(urls)}")

   result = dict()
   result[url] = sorted(urls)

   save_json(urlparse(url).hostname, result=result)

##########################
if __name__ == "__main__":
    main()
