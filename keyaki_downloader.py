from bs4 import BeautifulSoup
import urllib
import urllib.request
from urllib.parse import urlparse
from urllib.parse import urljoin
from urllib.request import urlretrieve
from os import makedirs
import os.path, time, re

test_files = {}

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

def get_savepath(url):
    o = urlparse(url)
    savepath = "./" + o.netloc + o.path
    if re.search(r"/$", savepath):
        savepath += "index.html"
    return savepath

def prepare_dir(dirpath):
    savedir = os.path.dirname(dirpath)

    if os.path.exists(dirpath): return 

    if not os.path.exists(savedir):
        print("mkdir=", savedir)
        makedirs(savedir)
    
def download_file(url, root):
    savepath = get_savepath(url)
    prepare_dir(savepath)

    if savepath in test_files: return
    test_files[savepath] = True

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
    root = "http://www.keyakizaka46.com/s/k46o"
    url = "http://www.keyakizaka46.com/s/k46o/artist/02"
    download_file(url, root)

