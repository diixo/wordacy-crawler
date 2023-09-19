import time
import sys
import re
import requests
import json
from collections import deque
from bs4 import BeautifulSoup

import urllib.error
from urllib.parse import urlparse, urljoin
from urllib.request import urlopen, Request
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
#pip install lxml

logging = True

class Crawler:

   def __init__(self):
      self.home = ""
      self.new = deque()
      self.all = set()
      self.unknown = set()
      self.skip = set()

   def save_json(self, filename="crawler.json", result = dict()):
      filepath = "./storage/" + filename
      for item in self.skip: self.all.discard(item)
      result[self.hostname()] = sorted(self.all)

      with open(filepath, 'w', encoding='utf-8') as fd:
         json.dump(result, fd, ensure_ascii=False, indent=3)

   def clear(self):
      self.new.clear()
      self.all.clear()
      self.unknown.clear()
      self.skip.clear()

   def is_url_valid(self, url_str:str)->bool:
      avoid = [ ".php", "#",
         ".pptx", ".ppt", ".xls", ".xlsx", ".xml", ".xlt", ".pdf", ".doc", ".docx",
         ".jpg", ".jpeg", ".png", ".svg", ".ico", ".bmp", ".gif", ".map", ".ttf",
         ".pps", ".webp", ".txt", ".cmd", ".md" ".js", ".json", ".css", ".scss",
         ".zip", ".tar", ".rar", ".gz", ".iso", ".exe", ".sfx", ".msi", ".cgi"]
      for i in avoid:
         if re.search(i, url_str): return False
      return True

   def add_new(self, url_str: str):
      url_str = url_str.strip('/')
      if not self.is_url_valid(url_str):
         self.skip.add(url_str)
      elif url_str not in self.all:
         #print(f"added new: {url_str}")
         self.new.append(url_str)
         self.all.add(url_str)

   def hostname(self):
      if self.home: return urlparse(self.home).hostname
      return self.home

   def extract_urls(self, raw):
      hostname = self.hostname()

      alls = raw.find_all(['a', 'loc'])
      for link in alls:
         if hasattr(link, 'attrs'):
               sref = link.attrs.get('href', None)
               if sref:
                  u_hostname = urlparse(sref).hostname
                  if (not u_hostname) or (u_hostname == hostname):  #as relative
                     ref = urljoin(self.home, sref)
                     self.add_new(ref)
                  else:
                     self.unknown.add(u_hostname)
                     #self.unknown.add(sref)

   def open_url(self, url:str, parser:str):
      try:
            req = Request(url, headers={'User-Agent': 'XYZ/3.0'})
            html = urlopen(req).read()
            raw = BeautifulSoup(html, features=parser)

            self.extract_urls(raw)
            return True
      except urllib.error.URLError as e:
            if hasattr(e, 'code'): print("URLErr_code:", e.code, f" ({url})")
            if hasattr(e, 'reason'): print("URLErr_reason:", e.reason)
      except urllib.error.HTTPError as e:
            if hasattr(e, 'code'): print("HTTPErr_code:", e.code, f" ({url})")
            if hasattr(e, 'reason'): print("HTTPErr_reason:", e.reason)
      except:
            print("Unexpected urlopen-error:", sys.exc_info()[0])
      self.skip.add(url)
      return False


   def run(self, domain: str):
      self.home = domain.strip('/')
      self.clear()
      self.add_new(self.home)
      counter = 0

      while(len(self.new) > 0):
         url = self.new.popleft()
         counter += 1

         with requests.Session() as session:

            retry = Retry(connect=3, backoff_factor=0.5)
            adapter = HTTPAdapter(max_retries=retry)
            session.mount('http://', adapter)
            session.mount('https://', adapter)

            Content_Type = session.head(url).headers["Content-Type"]
            
            if "text/html" in Content_Type:
               self.open_url(url, "html.parser")

            elif "text/xml" in Content_Type:
               if logging: print(f"...on: XML={url}")
               self.open_url(url, "xml")
               self.skip.add(url)

         if logging: print(f"...on: {counter} [queue={len(self.new)}, all={len(self.all)}, skipped={len(self.skip)}]")
         time.sleep(1.0)
      return self.all


def main():
   crawler = Crawler()
   #crawler.run("https://kotlinandroid.org/")
   #crawler.run("https://javascriptcode.org/")
   #crawler.save_json("javascriptcode.org.json")

   crawler.run("https://pythonexamples.org")
   crawler.save_json("pythonexamples.org.json")


if __name__ == "__main__":
   main()
