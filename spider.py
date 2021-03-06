from urllib.parse import urlencode
import requests
from pyquery import PyQuery as pq
import time
import os
import csv
import json
import sqlite3
import pymongo


base_url = 'https://m.weibo.cn/api/container/getIndex?'

headers = {
    'Host': 'm.weibo.cn',
    'Referer': 'https://m.weibo.cn/u/2830678474',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
}

class SaveCSV(object):

    def save(self, keyword_list,path, item):
        try:
            # 第一次打开文件时，第一行写入表头
            if not os.path.exists(path):
                with open(path, "w", newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=keyword_list)
                    writer.writeheader()  # 写表头
            # 写入内容
            with open(path, "a", newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keyword_list)
                writer.writerow(item)  # 写入数据
                print("success")

        except Exception as e:
            print("write error==>", e)
            # 记录错误数据
            with open("error.txt", "w") as f:
                f.write(json.dumps(item) + ",\n")
            pass

def get_page(page,title): #得到页面的请求，params是我们要根据网页填的，就是下图中的Query String里的参数
    params = {
        'containerid': '100103type=1&q='+title,
        'page_type': 'searchall',
        'page': page
    }
    proxies = {
        "http": None,
        "https": None
    }
    url = base_url + urlencode(params)
    print(url)
    try:
        response = requests.get(url, headers=headers, proxies=proxies)
        if response.status_code == 200:
            print(page)
            return response.json()
    except requests.ConnectionError as e:
        print('Error', e.args)

def parse_page(json,label):
    res=[]   #0:id 1:性别 2:地区 3:label 4:text
    if json:
        items = json.get('data').get('cards')
        for i in items:
            if i == None:
                continue
            item = i.get('mblog')
            if item == None:
                continue
            weibo = {}
            weibo['id'] = str(item.get('user').get("id"))
            weibo['label'] = label
            weibo['text'] = pq(item.get('text')).text().replace(" ", "").replace("\n", "")
            gender,place=getUserInfo(weibo['id'])
            weibo['gender']=gender
            weibo['place']=place
            res.append(weibo)
    return res


def getUserInfo(id):
    url = 'https://m.weibo.cn/api/container/getIndex?containerid=230283' + id + '_-_INFO'
    proxies = {
        "http": None,
        "https": None
    }
    response = requests.get(url, headers=headers, proxies=proxies)
    js = response.json()
    gender,place="None","None"
    if js:
        cards = js.get("data").get("cards")
        for card in cards:
            group = card.get("card_group")
            for item in group:
                if item.get("item_name") == "性别":
                    gender=item["item_content"]
                    continue
                if item.get("item_name") == "所在地":
                    place=item["item_content"]
                    continue
    return gender,place

if __name__=='__main__':
    title = input("请输入搜索关键词：")
    path = "data/article.csv"
    item_list=['id','gender','place','label','text']
    s=SaveCSV()
    for page in range(1,10):
        try:
            time.sleep(1)
            json=get_page(page,title)
            results=parse_page(json,title)
            if results==None:
                continue
            for result in results:
                if result is None:
                    continue
                print(result)
                s.save(item_list,path,result)
        except TypeError as e:
            print('error')
            continue
