import time

import requests

from bs4 import BeautifulSoup
import csv


def request_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/88.0.4324.146 Safari/537.36',
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
    except requests.RequestException:
        return None


# 定义存储变量
data = []


def parse_result(html, href):
    if html is None:
        return
    soup = BeautifulSoup(html, 'lxml')
    item_list = soup.find(class_="g-list").find_all(class_="list-item")
    for item in item_list:
        cache_data = ['', '', '', '', '', '', '', '', '']
        cache_data[0] = item.find('th').text
        print(item.find('th').text)
        td_list = item.find_all("td")
        for a in range(0, len(td_list)):
            cache_data[a + 1] = td_list[a].text.split("：")[1]
            print(td_list[a].text)
        cache_data[7] = item.find(class_="introduce").text
        cache_data[8] = href
        print(item.find(class_="introduce").text)
        data.append(cache_data)


def write_data(data_):
    print('开始写入数据 ====> ')
    # def create_csv():
    title_data = ['姓名', '性别', '居住地', '年龄', '薪资', '婚姻', '身高', '介绍', '原地址']
    with open('珍爱网威海1-10.csv', 'w', newline='', encoding='utf-8-sig') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(title_data)
        for info in data_:
            writer.writerow(info)

    csv_file.close()


def main(page):
    # 省结果公告地址
    url = 'https://www.zhenai.com/zhenghun/weihai/' + str(page)
    print('第{}页 ====> '.format(page))
    print(url)
    # 获取公告内容
    data_html = request_data(url)
    # 解析内容
    parse_result(data_html, url)


if __name__ == "__main__":
    for i in range(1, 11):
        main(i)
        time.sleep(2)

    write_data(data)
