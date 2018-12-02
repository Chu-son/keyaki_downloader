import requests
import sys

from bs4 import BeautifulSoup
import urllib
import urllib.request
from urllib.parse import urlparse
from urllib.parse import urljoin
from urllib.request import urlretrieve
from os import makedirs
import os.path, time, re

def extract_link(url):
    try:
        rr = requests.get(url)
        html = rr.content
        try:
            soup = BeautifulSoup(html, "html.parser")
            for aa in soup.find_all("a"):
                link = aa.get("href")
                name = aa.get_text()
                #print(name)
                print(" ",link)
        except Exception as ee:
            sys.stderr.write("*** error *** in BeautifulSoup ***\n")
            sys.stderr.write(str(ee) + "\n")
#

    except Exception as ee:
        sys.stderr.write("*** error *** in requests.get ***\n")
        sys.stderr.write(str(ee) + "\n")

def enum_links(html, base):
    soup = BeautifulSoup(html, "html.parser")
    links = soup.select("link[rel='stylesheet']")
    links += soup.select("a[href]")
    links += soup.select("img[src]")
    result = []

    for a in links:
        href = a.attrs['href']
        url = urljoin(base, href)
        result.append(url)
    return result

def download_file(url, root):
    try:
        print("download=", url)
        time.sleep(1)
        # メモリにDLして解析→保存に変える
        urlretrieve(url, savepath)
    except:
        print("ダウンロード失敗:", url)
        return None

    try:
        html = open(savepath, "r", encoding="utf-8").read()
        if "<html>" in html:
            links = enum_links(html, url)
            for link_url in links:
                if link_url.find(root) != 0:
                    if not re.search(r".css$", link_url): continue

                download_file(link_url, root)

    except:
        print("テキスト以外")

if __name__ == "__main__":
    url = "http://www.keyakizaka46.com/s/k46o/artist/02"
    extract_link(url)

