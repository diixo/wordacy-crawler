import time
import sys
import re
import requests
import ssl
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
import logging

#######################################
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

_logging = True

SSL_CONTEXT = ssl._create_unverified_context()
#######################################

def url_hostname(url_str:str):
   url_str = url_str.strip('/')
   host = urlparse(url_str)
   return host.scheme + "://" + host.hostname

class Crawler2:

   def __init__(self, delay = 3.0, recursive=False):
      self.hostnames = dict()
      #self.hostnames_pagination = []

      self.new = deque()
      self.skip = set()
      self.filters = dict()
      self.filepath = None
      self.urls = dict()
      self.recursive = recursive
      self.delay = delay


   def open_json(self, filepath:str):
      path = Path(filepath)
      if path.exists():
         fd = open(filepath, 'r', encoding='utf-8')
         self.urls = json.load(fd)
         for domain in self.urls.keys():
            self.urls[domain] = set(self.urls[domain])
         self.new = deque(self.urls.get(".new", deque()))
         print(f"<< [Crawler2]::open_json[remained={len(self.new)}]")
      self.filepath = filepath


   def save_json(self, filepath=None):

      if not filepath:
         filepath = self.filepath

      if not filepath: return

         # t = dt.now()
         # filename = f"{t.year}-{t.month}-{t.day}_{t.hour}-{t.minute}-{t.second}"#-{t.microsecond}"
         # filepath = "./test/" + filename + ".json"

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


   def open_hostnames(self, filepath:str):
      path = Path(filepath)
      if path.exists():
         fd = open(filepath, 'r', encoding='utf-8')
         self.hostnames = json.load(fd)
         #self.hostnames_pagination = list(self.hostnames.keys())
         print(f"<< [Crawler2]::open_hostnames={len(self.hostnames)}")

   def save_hostnames(self, filepath=None):
      if filepath == None:
         filepath = "db-hostnames.json"
      with open(filepath, 'w', encoding='utf-8') as fd:
         json.dump(self.hostnames, fd, ensure_ascii=False, indent=2)


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
            
            #if _logging: logger.info(f"add_new: {url_str}")


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
         #self.hostnames_pagination.append(u_hostname)

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
      #print("extract_urls: ", str(len(alls)))
      logger.info("find_all_urls: " + str(len(alls)))

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
                     elif _logging:
                        #print(f"[Crawler2] Unexpected syntax error: url={sref}")
                        logger.info(f"[Crawler2] Unexpected syntax error: url={sref}")
                  else:
                     #
                     if u_hostname not in self.hostnames:
                        self.hostnames[u_hostname] = { "urls":[], "type":"0" }
                        #self.hostnames_pagination.append(u_hostname)

                     findex = max(sref.find("?via="), sref.find("?ref="))
                     if findex > 0:
                        sref = sref[:findex]

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
            if _logging and (status in [301, 302]):
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

   def run_url(self, url:str):
      with requests.Session() as session:
         try:
            retry = Retry(connect=3, backoff_factor=0.5)
            adapter = HTTPAdapter(max_retries=retry)
            session.mount('http://', adapter)
            session.mount('https://', adapter)


            head = session.head(url)
            Content_Type = head.headers.get("Content-Type", "text/html")
            
            if "text/html" in Content_Type:
               self.open_url(url, "html.parser")

            elif "text/xml" in Content_Type:
               if _logging: print(f"[Crawler2] ...on: XML={url}")
               self.open_url(url, "xml")
               self.skip.add(url)
         except KeyboardInterrupt:
            print("KeyboardInterrupt exception raised")
         except:
            print("Unexpected error raised:", sys.exc_info()[0])


   def run(self):
      counter = 0

      while(len(self.new) > 0):
         url = self.new.popleft()
         counter += 1

         self.run_url(url=url)

         ###########
         if _logging: 
            print(f"[Crawler2] ...on: {counter}, [remained={len(self.new)}] [skipped={len(self.skip)}]")
            logger.info("[Crawler2] ...on: " + str(counter) + ", [remained=" + str(len(self.new)) + "]")
         time.sleep(self.delay)


   def get_urls(self, url: str = None):
      if url:
         return self.urls.get(url_hostname(url), [])
      else:
         return self.urls

###############################################################################################

   def __call__(self, url: str):
      self.run()
