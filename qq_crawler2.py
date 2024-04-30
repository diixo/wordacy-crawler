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


class ReversePaginator:
   def __init__(self, data, page_size):
      self.data = data
      self.page_size = page_size

   def get_page(self, page_index):
      result = []
      sz = len(self.data)

      start_index = max(sz - page_index * self.page_size, 0)
      end_index = sz - (page_index-1) * self.page_size
      #   if start_index < sz:
      #       end_index = min(page_index*self.page_size, sz)
      result = self.data[end_index - 1: start_index - 1 if start_index != 0 else None: -1]
      return result

   def num_pages(self):
      return (len(self.data) + self.page_size - 1) // self.page_size


logging = True

def url_hostname(url_str:str):
   url_str = url_str.strip('/')
   host = urlparse(url_str)
   return host.scheme + "://" + host.hostname

class Crawler2:

   def __init__(self, delay = 1.0, recursive=False):
      self.hostnames = dict()
      self.hostnames_indexing = []

      self.new = deque()
      self.skip = set()
      self.filters = dict()
      self.filepath = ""
      self.urls = dict()
      self.recursive = recursive
      self.delay = delay


   def open_json(self, filepath:str):
      path = Path(filepath)
      if path.exists():
         fd = open(filepath, 'r', encoding='utf-8')
         self.urls = json.load(fd)
         self.new = deque(self.urls.get(".new", deque()))
         print(f"<< [Crawler2]::open_json[remained={len(self.new)}]")
      self.filepath = filepath

   def open_hostnames(self, filepath:str):
      path = Path(filepath)
      if path.exists():
         fd = open(filepath, 'r', encoding='utf-8')
         self.hostnames = json.load(fd)
         self.hostnames_indexing = list(self.hostnames.keys())
         print(f"<< [Crawler2]::open_hostnames={len(self.hostnames)}")

   def save_hostnames(self, filepath=None):
      if filepath == None:
         filepath = "db-hostnames.json"
      with open(filepath, 'w', encoding='utf-8') as fd:
         json.dump(self.hostnames, fd, ensure_ascii=False, indent=2)


   def save_json(self, filepath=""):
      if not filepath:
         filepath = self.filepath
      if (filepath == ""):
         t = dt.now()
         filename = f"{t.year}-{t.month}-{t.day}_{t.hour}-{t.minute}-{t.second}"#-{t.microsecond}"
         filepath = "./test/" + filename + ".json"

      result = dict()
      for host in self.urls.keys():
         result[host] = sorted(self.urls[host])

      if (len(self.new) > 0):
         result[".new"] = list(self.new)
      else:
         result[".new"] = None
         result.pop(".new")

      with open(filepath, 'w', encoding='utf-8') as fd:
         json.dump(result, fd, ensure_ascii=False, indent=3)

      if len(self.skip) > 0:
         with open(filepath + ".skipped.txt", 'w', encoding='utf-8') as fd:
            json.dump(sorted(self.skip), fd, ensure_ascii=False, indent=3)

      # with open("db-hostnames-from.json", 'w', encoding='utf-8') as fd:
      #    json.dump(list(self.unknown_from), fd, ensure_ascii=False, indent=3)


   def clear(self):
      self.new.clear()
      self.urls.clear()
      self.hostnames.clear()
      self.skip.clear()
      self.filters.clear()

   def is_url_valid(self, url_str:str):
      avoid = [ ".php", "#", ".asp?", "mailto:", ".map", ".ttf",
         ".pptx", ".ppt", ".xls", ".xlsx", ".xml", ".xlt", ".pdf", ".doc", ".docx", ".chm",
         ".jpg", ".jpeg", ".png", ".svg", ".ico", ".bmp", ".gif", ".tiff", ".exif",
         ".pps", ".webp", ".txt", ".cmd", ".md" ".js", ".json", ".css", ".scss",
         ".zip", ".tar", ".rar", ".xz", ".gz", ".tgz", ".pkg", ".cab", ".jar", ".iso", 
         ".exe", ".sfx", ".msi", ".cgi", ".mp4"]
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
         #print(f"skipped(validation,filtered): {url_str}")
      elif url_str not in self.urls[hostname]:
         self.urls[hostname].add(url_str)
         if self.recursive:
            self.new.append(url_str)


   def enqueue_url(self, url_str: str, cntr = 1):
      url_str = url_str.strip('/')
      hostname = url_hostname(url_str)
      self.set_filter(url_str, [])

      if hostname not in self.urls:
         self.urls[hostname] = set()

      if url_str not in self.urls[hostname]:
         self.urls[hostname].add(url_str)
         self.new.append(url_str)

      if cntr > 1:
         for i in range (2, cntr+1):
            self.urls[hostname].add(url_str)
            self.new.append(url_str + "/page/" + str(i))


   def register_url(self, url):
      url = url.strip("/")
      u_hostname = urlparse(url).hostname

      if u_hostname not in self.hostnames:
         self.hostnames[u_hostname] = { "urls":[], "type":"1" }
         self.hostnames_indexing.append(u_hostname)

      hostname_ref = self.hostnames[u_hostname]
      linkset = set(hostname_ref["urls"])
      linkset.add(url)
      hostname_ref["urls"] = sorted(linkset)


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
                  sref = re.sub("http://", "https://", sref).strip().lower()
                  u_hostname = urlparse(sref).hostname
                  if (not u_hostname) or (u_hostname == hostname):  #as relative
                     ref = urljoin(home, sref)
                     if re.search(home, ref):
                        self.add_new(ref)
                     elif logging: print(f"[Crawler2] Unexpected syntax error: url={sref}")
                  else:
                     if u_hostname not in self.hostnames:
                        self.hostnames[u_hostname] = { "urls":[], "type":"0" }
                        self.hostnames_indexing.append(u_hostname)

                     if sref.find("="+"opentools") > 1:
                        sref = urlparse(url).scheme + '://' + u_hostname

                     hostname_ref = self.hostnames[u_hostname]
                     linkset = set(hostname_ref["urls"])
                     linkset.add(sref.strip("/"))
                     hostname_ref["urls"] = sorted(linkset)

                     #self.hostnames.add(u_hostname)
                     #self.hostnames.add(sref)


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
            if hasattr(e, 'code'):
               print("URLErr_code:", e.code, f"url={url}")
               if str(e.code) == "520":
                  self.new.append(url)
                  print(f"push again >> {e.code}_url:{url}")

            if hasattr(e, 'reason'): print("URLErr_reason:", e.reason, f"url={url}")

      except urllib.error.HTTPError as e:
            if hasattr(e, 'code'): print("HTTPErr_code:", e.code, f"url={url}")
            if hasattr(e, 'reason'): print("HTTPErr_reason:", e.reason, f"url={url}")
      except:
            print("Unexpected urlopen-error:", sys.exc_info()[0])
      self.skip.add(url)
      #print(f"skipped(open_url): {url}")


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
                  #print(f"skipped(run_type): {url}")
            if logging: print(
               f"[Crawler2] ...on: {counter}, [remained={len(self.new)}] [skipped={len(self.skip)}] [hosts={len(self.hostnames)}]")
            time.sleep(self.delay)
      except KeyboardInterrupt:
         print("KeyboardInterrupt exception raised")
      except:
         print("Unexpected error raised:", sys.exc_info()[0])

   def get_urls(self, url: str = None):
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
   crawler.open_json("test/www.unite.ai.json")

   crawler.set_filter("https://www.unite.ai/", [
      "mailto:",
      "javascript:",
      "/author",
      "/blogger",
      "/user/login",
      "/privacy-policy",
      "/terms-and-conditions",
      "/contact-us",
      "/meet-the-team",
      "/press-tools",
      "/imagesai",
      "/our-cherter",
      "/cdn-cgi",
      "/?", "=%", "/%", 
      "/de/", "/es/", "/fr/", "/id/", "/it/", "/ja/", "/ko/", "/nl/", "/no/", "/pl/", "/pt/", "/ru/", "/tr/", "/vi/",
      "/about",
      "/affiliate-terms",
      "/agencies",
      "/careers",
      "/compatibilities",
      "/contact",
      "/contactus",
      "/features",
      "/integrations",
      "/partner",
      "/partner-apply",
      "/pricing",
      "/privacy",
      "/refunds",
      "/terms",
      "/enterprise",
      "/faq",
      "/how-does-it-work",
      "/privacy",
      "/terms",
      "/partner",
      "/price",
      "/support"
      ])
   crawler.run()
   crawler.save_json("test/www.unite.ai.json")

def main():
   test_unite_ai()
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
