from urllib.parse import urlencode
import requests
import time
import json
import os
import re
from hashlib import md5
from config import *

from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from requests import codes

headers = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",
    "cookie":"csrftoken=38cedc6f487e55e7ca07184f4868d64c; tt_webid=6693443342992344583; __tasessionId=87eayfdge1558529566969; s_v_web_id=677421d9182b24ed6646b5dc4362ca64"
}
def get_page_index(offset=0,keyword="街拍"):
    data = {
        "aid": 24,
        "app_name": "web_search",
        "offset": offset,
        "format":"json",
        "keyword": keyword,
        "autoload": "true",
        "count": 20,
        "en_qc": 1,
        "cur_tab": 1,
        "from": "search_tab",
        "pd": "synthesis",
        "timestamp": str(int(time.time()))
    }
    url = "https://www.toutiao.com/api/search/content/?" + urlencode(data)
    try:
        response = requests.get(url,headers=headers)
        if 200 == response.status_code:
            return response.json()
        return None
    except RequestException:
        print("请求失败,请求索引页出错")
        return None
# 解析索引页json数据
def parse_page_index(html):
    data = html
    if data and 'data' in data.keys(): # data 是否存在，data的键值对是否有‘data’
        for item in data.get('data'):
            yield item.get('article_url') # 构造生成器

# 获取详情页
def get_page_detail(url):
    try:
        r = requests.get(url, headers=headers)
        if 200 == r.status_code:
            return r.text
        return None
    except RequestException:
        print("获取详情页出错！")

def parse_page_detail(html,url):
    soup = BeautifulSoup(html,"lxml")
    title = soup.select('title')[0].get_text()
    print(url)  # 打印链接
    print(title) #打印标题
    images_pattern = re.compile('gallery: JSON.parse\(\"(.*?)\"\),',re.S)
    result = re.search(images_pattern,html)
    if result:
        #print(type(result.group(1)))
        try:
            data = json.loads(result.group(1))
            if data and 'sub_images' in data.keys():
                sub_images = data.get("sub_images")
                images = [item.get("url") for item in sub_images]
                return {
                    "title":title,
                    "url":url,
                    "images":images
                }
            else:
                return None
        except json.decoder.JSONDecodeError:
            pass
            return None
    else:
        content_pattern = re.compile('.*?(http:.*?)&quot;',re.S)
        result = re.findall(content_pattern, html)
        if result:
            return {
                "title":title,
                "url":url,
                "images":result[1:]
            }
        else:
            return None

def download(url,title):
    root = os.getcwd() + "\\img\\"+title+"\\"
    try:
        if not os.path.exists(root):
            os.makedirs(root) #创建多级目录文件夹

        r = requests.get(url, headers=headers)
        file_name = root+md5(r.content).hexdigest()+".jpg"
        if not os.path.exists(file_name):
            with open(file_name, 'wb') as f:
                f.write(r.content)
                print("保存成功！")
                f.close()
    except:
        print("保存失败！")


def main():
    html = get_page_index(0,"街拍")
    for url in parse_page_index(html):
        if url and url.startswith("http://toutiao.com/group"):
            html = get_page_detail(url)
            if html:
                result = parse_page_detail(html,url)
                #print(result) #打印None
                if result:
                    title = result["title"]
                    for image_url in result["images"]:
                        download(image_url,title)



if __name__ == "__main__":
   main()