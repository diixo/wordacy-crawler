import urllib.request
import urllib.parse
import time
import codecs

#import lxml.html

from urllib.parse import urlparse

#import sys
#import codecs

import os
import io

try:
    from BeautifulSoup import BeautifulSoup, NavigableString
except ImportError:
    from bs4 import BeautifulSoup, NavigableString #pip3 install BeautifulSoup4

#file_train_db = io.open("train-DB.html",'w', encoding='utf-8')
file_train_db = open("techopedia-train-db.txt", 'w', encoding='utf-8')

test = "C:\\DownloadedWebSites\\www.techopedia.com\\definition\\26184\\c-plus-plus-programming-language.html"
test = "C:/DownloadedWebSites/www.techopedia.com/2/27749/personal-tech/5-psychological-tricks-video-games-use-to-keep-you-playing.html"

test = "C:/DownloadedWebSites/www.techopedia.com/definition/16523/trusted-computing.html"

test = "C:/DownloadedWebSites/www.techopedia.com/10-essential-computer-science-courses-you-can-take-online/2/33880.html"

test = "C:/DownloadedWebSites/www.techopedia.com/2/28629/internet/social-media/7-sneaky-ways-hackers-can-get-your-facebook-password.html"


#test = BeautifulSoup(open("C:\\DownloadedWebSites\\www.techopedia.com\\definition\\26184\\c-plus-plus-programming-language.html"), "html.parser")

#raw = BeautifulSoup(open("C:/DownloadedWebSites/www.techopedia.com/women-in-tech-entrepreneurs-resilient-intuitive-and-playing-it-forward/2/34207.html"), "html.parser")

#########################
def parseFile(filename):
    global file_train_db

    raw = BeautifulSoup(open(filename, encoding='utf-8'), "html.parser")

    h1 = raw.body.find('h1', attrs={'role': 'heading'})

    if h1 is None:
        return

    #print("=" + h1.text)

    file_train_db.write("<item>" + '\n')
    file_train_db.write(f"<uri>{filename[22:]}</uri>\n")
    file_train_db.write("<h1>" + '\n')
    file_train_db.write(h1.text.strip())
    file_train_db.write('\n' + "</h1>" + '\n')

    #############################################################################
    #definition = raw.body.find('nav', attrs={'class': 'mb-2'})
    #if definition:
    #    a_list = definition.find_all('li')

    #    sz = len(a_list)

    #    if (sz > 0): file_train_db.write("<def>" + a_list[sz-1].text.strip() + "</def>" + '\n')

    #    file_train_db.flush()
    ############################################################################
    article_array = raw.body.find_all('div', attrs={'class':'jan-article__content'})

    for item in article_array:
        contents = item.contents

        for content in contents:
            if hasattr(content, 'attrs') and hasattr(content, 'name'):

                if content.name == 'h2' and 'role' in content.attrs:
                    #print("==" + content.text)
                    txt = content.text.strip()
                    if txt:
                        file_train_db.write("<h2>" + '\n')
                        file_train_db.write(txt)
                        file_train_db.write('\n' + "</h2>" + '\n')
                elif content.name == 'p' and 'data-empty' in content.attrs:
                    #print(content.text)
                    txt = content.text.strip()
                    if txt:
                        file_train_db.write("<p>" + '\n')
                        file_train_db.write(txt)
                        file_train_db.write('\n' + "</p>" + '\n')
                elif content.name == 'ul' or content.name == 'ol':
                    #print(content.text)
                    file_train_db.write("<ul>" + '\n')
                    for li in content.contents:
                        if hasattr(li, 'name'):
                            if li.name == 'li': file_train_db.write("<li>" + li.text.strip() + '</li>\n')
                    file_train_db.write("</ul>" + '\n')
                elif content.name == 'p' and 'dir' in content.attrs:
                    #print(content.text)
                    txt = content.text.strip()
                    if txt:
                        file_train_db.write("<p>" + '\n')
                        file_train_db.write(txt)
                        file_train_db.write('\n' + "</p>" + '\n')
                elif content.name == 'p' and not ('dir' in content.attrs) and not ('data-empty' in content.attrs):
                    if content.text:# or content.text != "":
                        #print("p0 " + content.text)
                        txt = content.text.strip()
                        if txt:
                            file_train_db.write("<span>" + '\n')
                            file_train_db.write(txt)
                            file_train_db.write('\n' + "</span>" + '\n')
                elif content.name == 'div':
                    if 'class' in content.attrs:
                        if (content.attrs['class'][0] == "ad__wrapper") or (content.attrs['class'][0] == "mt-5"):
                            #content.text:  # or content.text != "":
                            #print("adv: ")
                            None
                        elif content.text:
                            #print("p0 " + content.text)
                            txt = content.text.strip()
                            if txt:
                                file_train_db.write("<span>" + '\n')
                                file_train_db.write(txt)
                                file_train_db.write('\n' + "</span>" + '\n')
                    elif content.text:# or content.text != "":
                        #print("p0 " + content.text)
                        txt = content.text.strip()
                        if txt:
                            file_train_db.write("<span>" + '\n')
                            file_train_db.write(txt)
                            file_train_db.write('\n' + "</span>" + '\n')

            #else:
            #    if isinstance(content, NavigableString):
            #        print(content.string)


    #article_array = raw.body.find_all('div', attrs={'class': 'jan-article'})
    #for article in article_array:
    #    file_train_db.write("<article>" + '\n')
    #    file_train_db.write(article.text)
    #    file_train_db.write('\n' + "</article>" + '\n')

    related_array = raw.body.find_all('div', attrs={'class':'mt-5'})

    # related items
    print("---------- related items:")
    for related in related_array:
        h4 = related.find('h4')
        if (h4 is not None):
            lst = related.find_all('li', attrs={'class':'list-group-item'})
            len4 = len(lst)
            for lst_item in lst:
                #print(lst_item.text)
                file_train_db.write("<h4>" + '\n')
                file_train_db.write(lst_item.text)
                file_train_db.write('\n' + "</h4>" + '\n')



    # tags items
    print("---------- tags:")
    tags_array = raw.body.find_all('a', attrs={'class':'btn btn-link border mb-2 mr-3'})
    for tag in tags_array:
        #print(tag.text)
        file_train_db.write("<tag>" + '\n')
        file_train_db.write(tag.text)
        file_train_db.write('\n' + "</tag>" + '\n')

    file_train_db.write("</item>" + '\n')

    file_train_db.flush()
########################

path ="C:/DownloadedWebSites/www.techtarget.com"
path ="C:/DownloadedWebSites/www.techopedia.com"
def list_dir(dir_path):
    i = 0
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if (file.endswith(".html")):
                print(os.path.join(root, file))
                parseFile(os.path.join(root, file))
                i += 1
                print(i)



list_dir(path)
#parseFile(test)
file_train_db.flush()
file_train_db.close()
print("closed")
