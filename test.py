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


savepath_root = "./root/"

def get_soup(path):
    #time.sleep(1)
    #rr = requests.get(url)
    #html = rr.content
    with open(path, 'r', encoding="UTF-8") as f:
        html = f.read()
    soup = BeautifulSoup(html, "lxml")

    return soup, html

def get_html_links(soup):
    link_list = [all_a.get("href") for all_a in soup.find_all("a")]
    return link_list

def get_content_links(soup):
    link_list = []
    for all_img in soup.find_all("img"):
        link = all_img.get("src")
        if not link is None:
            link_list.append(link)

    return link_list

ignore_query_list = [
        "ima",
        "dy",
        ]
def to_localpath(url, root = "./"):
    parse = urlparse(url)
    sp_path = os.path.splitext(parse.path)
    query = '&'.join([q for q in parse.query.split('&') if not q.split('=')[0] in ignore_query_list])
    query = '&' + query if not query == '' else query
    return root + parse.netloc + sp_path[0] + query + sp_path[1]

def to_absolute_url(url, baseurl):
    return urljoin(baseurl, url)

def save_contents(url, path, sleeptime = 1):
    print(url)
    time.sleep(sleeptime)

    prepare_dir(path)

    rr = requests.get(url)
    with open(path, 'wb') as f:
        f.write(rr.content)

    #urlretrieve(url, path)

def prepare_dir(path):
    savedir = os.path.dirname(path)
    if not os.path.exists(savedir):
        makedirs(savedir)

def is_external_site(url, baseurl): 
    return not urlparse(url).netloc == urlparse(baseurl).netloc

search_list = [
        "http://www\.keyakizaka46.com/s/k46o/search/",
        "http://www\.keyakizaka46.com/s/k46o/diary/member/.*&ct=02",
        "http://www\.keyakizaka46.com/s/k46o/diary/member/.*&ct=1[09]",
        "http://www\.keyakizaka46.com/s/k46o/diary/detail/",
        "http://www\.keyakizaka46.com/s/k46o/artist/02",
        "http://www\.keyakizaka46.com/s/k46o/artist/1[09]",
        ]
def is_search_url(url):
    for search_url in search_list:
        #if urlparse(search_url).path in urlparse(url).path:
        if re.match(search_url, url):
            return True
    return False

exclusion_path = [
        "http://www.keyakizaka46.com/s/k46o/diary/tv",
        "http://www.keyakizaka46.com/s/k46o/artist/00/discography",
        ]
exclusion_quety = [
        "cd=report",
        "cd=event",
        ]
def is_exclusion_url(url):
    for ex_path in exclusion_path:
        if urlparse(ex_path).path in urlparse(url).path:
            return True
    for ex_query in exclusion_quety:
        if ex_query in urlparse(url).query:
            return True
    return False

def replace_link2localpath(html, link, localpath_dist, localpath_src):
    relpath_dist = os.path.relpath(localpath_dist, os.path.dirname(localpath_src))
    return html.replace(link, relpath_dist)

def save_replaced_html(html, localpath):
    if os.path.splitext(localpath)[1] == '':
        localpath = localpath + ".html"
    prepare_dir(localpath)
    with open(localpath, "w", encoding = "UTF-8") as f:
        f.write(html)

    return localpath

exclusion_path_list = set()
def download(url, baseurl):
    url = to_absolute_url(url, baseurl)
    if is_external_site(url, baseurl):return
    if not is_search_url(url) or is_exclusion_url(url):
        exclusion_path_list.add(urlparse(url).path)
        return

    html_src_path = to_localpath(url, savepath_root + "src/")
    if os.path.exists(html_src_path):return html_src_path
    html_local_path = to_localpath(url, savepath_root + "local/")

    save_contents(url, html_src_path, sleeptime = 1)
    soup, html = get_soup(html_src_path)

    html_links = get_html_links(soup.body)
    for link in html_links:
        localpath_link_dist = download(link, baseurl)
        #print("link=",link)
        if localpath_link_dist is not None:
            html = replace_link2localpath(html, link, localpath_link_dist, html_src_path)

    content_links = get_content_links(soup)
    for link in content_links:
        localpath = to_localpath(link, savepath_root + "src/")
        if not os.path.exists(localpath):
            save_contents(link, localpath)

        html = replace_link2localpath(html, link, localpath, html_local_path)

    link_replaced_path = save_replaced_html(html, html_local_path)
    return link_replaced_path 

if __name__ == "__main__":
    url = "http://www.keyakizaka46.com/s/k46o/search/artist"
    url2 = "http://www.keyakizaka48.com/s/k46o/search/artist"
    url3 = "http://www.keyakizaka46.com/s/k46o/page/newmember?ima=0000#member-43"
    url4 = "http://www.keyakizaka46.com/s/k46o/diary/member/list?ima=0000&ct=02"
    url5 = "http://www.keyakizaka46.com/s/k46o/diary/member/list?ima=0000&page=2&cd=member&ct=02"
    url6 = "http://www.keyakizaka46.com/s/k46o/diary/member/list?ima=0000&ct=07"
    url7 = "http://www.keyakizaka46.com/s/k46o/diary/member/list?ima=0000&ct=19"

    #print(urljoin(url, "https://www.keyakizaka48.com/member/02"))
    #extract_link(url)
    #print(is_external_site(url, url2))
    #print(is_search_url(url3))
    #print(to_localpath(url6))

    #print(is_search_url(url))

    download(url, url)
    [print(url) for url in exclusion_path_list]


