# -*- coding: utf-8 -*-
# !/usr/bin/python
# @Time    : 2021-04-07
# @Author  : 
# @FileName: fofa_spider.py
# version: 1.0.3无限抓取版
# 04-08 增加百尾时间戳打印

import requests
import base64
import re
import config
import random
from urllib.parse import quote
import datetime
from datetime import datetime
from datetime import timedelta
import time

host_list = []
timestamp_list = []


def logo():
    print(r'''
  _____       _____                        .__    .___            
_/ ____\_____/ ____\____      ____________ |__| __| _/___________ 
\   __\/  _ \   __\\__  \    /  ___/\____ \|  |/ __ |/ __ \_  __ \
 |  | (  <_> )  |   / __ \_  \___ \ |  |_> >  / /_/ \  ___/|  | \/
 |__|  \____/|__|  (____  / /____  >|   __/|__\____ |\___  >__|   
                        \/       \/ |__|           \/    \/       
                                            version 1.0.3 无限抓取版
    ''')


def check_cookie():
    if config.fofa_token == "":
        print("[*] 请配置config fofa_token文件")
        exit(0)
    print("[*] 检测到fafa_token，请保证token可用")
    return


def headers():
    user_agent_use = config.user_agent[random.randint(0, len(config.user_agent) - 1)]
    headers_use = {
        'User-Agent': user_agent_use,
        'Accept': 'application/json, text/plain, */*',
        'Authorization': config.fofa_token
    }
    return headers_use


def search_key_input():
    search_key = input('[*] 请输入fofa搜索关键字: ')
    search_key = '\"' + search_key + '\"'
    return search_key


def get_page_num(search_key):
    headers_use = headers()
    searchbs64 = quote(str(base64.b64encode(search_key.encode()), encoding='utf-8'))

    print("[*] 爬取页面为:https://fofa.so/result?&qbase64=" + searchbs64)
    html = requests.get(url="https://fofa.so/result?&qbase64=" + searchbs64, headers=headers_use).text
    pagenum = re.findall('<li class="number">(\d*)</li></ul><button type="button" class="btn-next">', html)
    print("[*] 该关键字存在页码: " + pagenum[0] + '页')
    return searchbs64, headers_use


def modify_search_url(search_key):
    global timestamp_list
    # timestamp_length = len(timestamp_list)
    if timestamp_list[-1] == timestamp_list[0]:
        time_before = timestamp_list[-1].strip('\n').strip()
    else:
        time_last = timestamp_list[-1].split(' ')[0].strip('\n').strip()
        # print(time_last)
        time_last_time = datetime.strptime(time_last, "%Y-%m-%d").date()
        # print(str(time_last_time))
        time_before = (time_last_time - timedelta(days=1))
        # print('time_before' + str(time_before))
    if 'before' in search_key:
        search_key = search_key.split('&& before')[0]
        search_key = search_key.strip(' ')
        search_key = search_key + ' && ' + 'before="' + str(time_before) + '"'
    else:
        search_key = search_key + ' && ' + 'before="' + str(time_before) + '"'
    search_key_modify = search_key
    searchbs64_modify = quote(str(base64.b64encode(search_key_modify.encode()), encoding='utf-8'))
    # print('[*] 搜索词： ' + search_key_modify)

    return search_key_modify, searchbs64_modify


def fofa_spider_page(page, search_key, searchbs64, headers_use, turn_num):

    global host_list
    global timestamp_list
    searchurl = quote(search_key)# searchurl是search_key url encode
    print("[*] 正在爬取第" + str(5*int(turn_num) + int(page)) + "页" + '\n')
    request_url = 'https://api.fofa.so/v1/search?q=' + searchurl + '&qbase64=' + searchbs64 + '&full=false&pn=' + str(page) + '&ps=10'
    page_json = requests.get(request_url, headers=headers_use).json()
    page_data = page_json['data']['assets']
    # print(type(page_json))
    # print(page_json.keys())
    # doc_result = open('fofa_result.txt', 'a+')
    for i in range(len(page_data)):
        host_data = page_data[i]['link']
        host_time = page_data[i]['mtime']
        timestamp_list.append(host_time)
        # doc_result.write(host_data + '\n')
        if host_data not in host_list:
            host_list.append(host_data)
        # html_time = page_data[i]['mtime']
        print('[+] ' + host_data)
    print()
    try:
        print('[*] 第' + str(5*int(turn_num) + int(page)) + '页爬取完毕 抓取数据' + str(i + 1) + '条 最后一条数据时间戳为：' + str(timestamp_list[-1]) + '\n')
    except UnboundLocalError:
        print('[*] 发生错误，请检查cookie信息是否为最新')
    except Exception as error:
        print(str(error))

    time.sleep(config.time_sleep)
    return


def fofa_spider(search_key, searchbs64, headers_use):
    global host_list

    start_page = input("[*] 请输入开始页码: ")
    want_page = input("[*] 请输入终止页码: ")
    print()
    if int(want_page) <= 5 and int(want_page) > 0:
        stop_page = want_page
        for page in range(int(start_page), int(stop_page) + 1):
            fofa_spider_page(page, search_key, searchbs64, headers_use, turn_num=0)
    elif int(want_page) > 5:
        if int(want_page) % 5 == 0:
            start_page = start_page
            stop_page = 5
            for turn_num in range(int(int(want_page)/5)):

                global timestamp_list
                # print('[*] 第 ' + str(turn_num + 1) + ' turn抓取')
                timestamp_list.clear()
                for page in range(int(start_page), int(stop_page) + 1):
                    fofa_spider_page(page, search_key, searchbs64, headers_use, turn_num)

                search_key_modify, searchbs64_modify = modify_search_url(search_key)
                search_key = search_key_modify
                searchbs64 = searchbs64_modify
        else:
            turn_sum = int(want_page) // 5
            page_last = int(want_page) % 5
            for turn_num in range(int(want_page) // 5):
                start_page = start_page
                
                stop_page = 5

                # print('[*] 第 ' + str(turn_num + 1) + ' turn抓取')
                timestamp_list.clear()
                for page in range(int(start_page), int(stop_page) + 1):
                    fofa_spider_page(page, search_key, searchbs64, headers_use, turn_num)

                search_key_modify, searchbs64_modify = modify_search_url(search_key)
                search_key = search_key_modify
                searchbs64 = searchbs64_modify
            for page in range(1, page_last + 1):
                # print('[*] 第 ' + str(turn_num + 2) + ' turn抓取')
                fofa_spider_page(page, search_key, searchbs64, headers_use, turn_num=turn_sum)
    else:
        print('[*] 输入错误')
        exit(0)
    return


def host_list_print():
    global host_list
    print('++++++++++++++++++++++++++++++++\n')
    doc_result = open('spider_result.txt', 'a+')
    for host in host_list:
        print('[+] ' + host)
        doc_result.write(host + '\n')
    doc_result.close()
    print()
    print('[+] 抓取结束，共抓取数据 ' + str(len(host_list)) + ' 条\n')
    return


def main():
    logo()
    check_cookie()
    search_key = search_key_input()
    searchbs64, headers_use = get_page_num(search_key)
    fofa_spider(search_key, searchbs64, headers_use)
    host_list_print()
    return


if __name__ == '__main__':
    main()
