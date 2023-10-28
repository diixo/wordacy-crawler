import time
import sys
import re
import requests
import json
from datetime import datetime as dt
from collections import deque
from bs4 import BeautifulSoup
from pathlib import Path

import urllib.error
from urllib.parse import urlparse, urljoin
from urllib.request import urlopen, Request
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
#pip install lxml

logging = True

def url_hostname(url_str:str):
   url_str = url_str.strip('/')
   host = urlparse(url_str)
   return host.scheme + "://" + host.hostname

class Crawler2:

   def __init__(self, recursive=False):
      self.new = deque()
      self.unknown = set()
      self.skip = set()
      self.filters = dict()
      self.filepath = ""
      self.urls = dict()
      self.recursive = recursive

   def open_json(self, filepath:str):
      path = Path(filepath)
      if path.exists():
         fd = open(filepath, 'r', encoding='utf-8')
         self.urls = json.load(fd)
      
      self.filepath = filepath

   def save_json(self, filepath=""):
      if not filepath:
         filepath = self.filepath
      if (filepath == ""):
         t = dt.now()
         filename = f"{t.year}-{t.month}-{t.day}_{t.hour}-{t.minute}-{t.second}"#-{t.microsecond}"
         filepath = "./storage/" + filename + ".json"

      result = dict()
      for host in self.urls.keys():
         result[host] = sorted(self.urls[host])

      with open(filepath, 'w', encoding='utf-8') as fd:
         json.dump(result, fd, ensure_ascii=False, indent=3)

      if len(self.skip) > 0:
         with open(filepath + ".skipped.txt", 'w', encoding='utf-8') as fd:
            json.dump(sorted(self.skip), fd, ensure_ascii=False, indent=3)


   def clear(self):
      self.new.clear()
      self.urls.clear()
      self.unknown.clear()
      self.skip.clear()
      self.filters.clear()

   def is_url_valid(self, url_str:str):
      avoid = [ ".php", "#", ".asp?", "mailto:", ".map", ".ttf",
         ".pptx", ".ppt", ".xls", ".xlsx", ".xml", ".xlt", ".pdf", ".doc", ".docx", ".chm",
         ".jpg", ".jpeg", ".png", ".svg", ".ico", ".bmp", ".gif", ".tiff", ".exif",
         ".pps", ".webp", ".txt", ".cmd", ".md" ".js", ".json", ".css", ".scss",
         ".zip", ".tar", ".rar", ".xz", ".gz", ".tgz", ".pkg", ".cab", ".jar", ".iso", 
         ".exe", ".sfx", ".msi", ".cgi"]
      for i in avoid:
         if str.find(url_str, i) >= 0: return False
      return True

   def is_filtered(self, url_str:str):
      hostname = url_hostname(url_str)
      filter = self.filters.get(hostname, [])
      for f in filter:
         if str.find(url_str + "/", f) >= 0: return True
      return False

   def set_filter(self, url_str: str, filter=[]):
      hostname = url_hostname(url_str)
      self.filters[hostname] = filter

   def add_new(self, url_str: str):
      url_str = url_str.strip('/')
      hostname = url_hostname(url_str)

      if not self.is_url_valid(url_str) or self.is_filtered(url_str):
         self.skip.add(url_str)
      elif url_str not in self.urls[hostname]:
         self.urls[hostname].add(url_str)
         if self.recursive:
            self.new.append(url_str)


   def enqueue_url(self, url_str: str):
      url_str = url_str.strip('/')
      hostname = url_hostname(url_str)
      self.set_filter(url_str, [])

      if hostname not in self.urls:
         self.urls[hostname] = set()

      if url_str not in self.urls[hostname]:
         self.urls[hostname].add(url_str)
         self.new.append(url_str)


   def extract_urls(self, raw, url):
      host = urlparse(url)
      hostname = host.hostname
      home = host.scheme + '://' + hostname
      #home = host[0] + '://' + host[1]

      alls = raw.find_all(['a', 'loc'])
      for link in alls:
         if hasattr(link, 'attrs'):
               sref = link.attrs.get('href', None)
               if sref:
                  sref = re.sub("http://", "https://", sref).strip()
                  u_hostname = urlparse(sref).hostname
                  if (not u_hostname) or (u_hostname == hostname):  #as relative
                     ref = urljoin(home, sref)
                     if re.search(home, ref):
                        self.add_new(ref)
                     elif logging: print(f"[Crawler2] Unexpected syntax error: url={sref}")
                  else:
                     #self.unknown.add(u_hostname)
                     self.unknown.add(sref)

   def open_url(self, url:str, parser:str):
      try:
            req = Request(url, headers={'User-Agent': 'XYZ/3.0'})
            response = urlopen(req)
            status = response.status
            if logging and (status in [301, 302]):
               print(f"[Crawler2] new_url = {response.geturl()}")
            html = response.read()

            raw = BeautifulSoup(html, features=parser)

            self.extract_urls(raw, url)
            return True
      except urllib.error.URLError as e:
            if hasattr(e, 'code'): print("URLErr_code:", e.code, f"url={url}")
            if hasattr(e, 'reason'): print("URLErr_reason:", e.reason, f"url={url}")
      except urllib.error.HTTPError as e:
            if hasattr(e, 'code'): print("HTTPErr_code:", e.code, f"url={url}")
            if hasattr(e, 'reason'): print("HTTPErr_reason:", e.reason, f"url={url}")
      except:
            print("Unexpected urlopen-error:", sys.exc_info()[0])
      self.skip.add(url)


   def extract_from_file(self, filepath:str, domain:str, filter=[]):
      self.clear()
      home = url_hostname(domain)

      if home not in self.urls:
         self.urls[home] = set()

      self.set_filter(domain, filter=filter)
      self.filepath = "./storage/" + urlparse(home).hostname + ".json"
      print(f"<< filepath = {self.filepath}")
      raw = BeautifulSoup(open(filepath, encoding='utf-8'), features="html.parser")
      self.extract_urls(raw, domain)


   def run(self):
      counter = 0
      try:
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
                  if logging: print(f"[Crawler2] ...on: XML={url}")
                  self.open_url(url, "xml")
                  self.skip.add(url)
            if logging: print(f"[Crawler2] ...on: {counter}, [remained={len(self.new)}] [skipped={len(self.skip)}]")
            time.sleep(1.0)
      except KeyboardInterrupt:
         print("KeyboardInterrupt exception raised")
      except:
         print("Unexpected error raised:", sys.exc_info()[0])

   def get_urls(self, url: str):
      if url:
         return self.urls.get(url_hostname(url), [])
      else:
         return self.urls

###############################################################################################

def test_futuretools():
   crawler = Crawler2()
   crawler.extract_from_file("./test/futuretools.html", "https://www.futuretools.io/", 
      ["/submit-a-tool", "/?d", "/faq", "/learn", "/?tags="])
   crawler.save_json()

def test_unite_ai():
   crawler = Crawler2(recursive=True)
   crawler.enqueue_url("https://www.unite.ai/")
   crawler.run()
   crawler.save_json()

def main():

   return

   crawler = Crawler2(recursive=False)
   crawler.open_json("test/crawler-2.json")

   crawler.enqueue_url("https://www.pythontutorial.net/python-concurrency/")
   crawler.set_filter("https://www.pythontutorial.net", ["/privacy-policy", "/contact", "/donation"])

   crawler.enqueue_url("https://kotlinandroid.org/kotlin/kotlin-hello-world/")
   crawler.set_filter("https://kotlinandroid.org", ["/privacy-policy", "/contact-us", "/terms-of-use"])

   crawler.run()
   crawler.save_json()

###############################################################################################
if __name__ == "__main__":
   main()
