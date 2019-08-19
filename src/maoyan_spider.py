import json
import time
from multiprocessing import Pool
from multiprocessing import Lock
import requests
from requests.exceptions import RequestException
import re
headers = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36"
}
#定义一个请求单页的方法
def get_one_page(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None

def parse_one_page(html):
    pattern = re.compile('<dd>.*?board-index.*?>(\d+)</i>.*?data-src="(.*?)".*?name"><a'
                         +'.*?>(.*?)</a>.*?star">(.*?)</p>.*?releasetime">(.*?)</p>'
                         +'.*?integer">(.*?)</i>.*?fraction">(.*?)</i>.*?</dd>',re.S)#re.S表示匹配任意字符,可以匹配换行符
    items = re.findall(pattern,html)
    #变成生成器
    for item in items:
        yield {
            'index':item[0],
            #"image":item[1],
            "title":item[2],
            "actor":item[3].strip()[3:],
            "time":item[4].strip()[5:],
            "score":item[5]+item[6]
        }

def write_to_file(content):
    #如果没有encoding json持久化的时候会对中文编码
    with open("result.txt","a",encoding="utf-8") as f:
        f.write(json.dumps(content,ensure_ascii=False) + "\n")
        f.close()

def main(offset = 0):
    url = "https://maoyan.com/board/4?offset="+ str(offset)
    html = get_one_page(url)
    for item in parse_one_page(html):
        print(item)
        write_to_file(item)


if __name__ == "__main__":
    start = time.time()
    #单线程for循环3秒钟
    # for i in range(0,100,10):
    #     main(i)

    pool = Pool()
    pool.map(main,[i for i in range(0,100,10)])
    end = time.time()
    #pool.close()
    #pool.join()
    print("耗时: %f" % (end - start))