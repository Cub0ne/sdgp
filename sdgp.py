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

domain = "http://www.ccgp-shandong.gov.cn"


def parse_announcement(html):
    if html is None:
        return []

    soup = BeautifulSoup(html, 'lxml')
    href_list = soup.select('a[href^="/sdgp2017/site/listcontnew.jsp?colcode=0302&"]')
    urls = []
    for href in href_list:
        # print(domain + href.get('href'))
        urls.append(domain + href.get('href'))
    return urls


def parse_result(html, href):
    cache_data = ['', '', '', '', '', '', '', '']
    if html is None:
        return
    soup = BeautifulSoup(html, 'lxml')
    title = soup.find('h1', class_="title").text
    # print(title)
    cache_data[0] = title

    table_list = soup.find(id='textarea').find_all("table")
    td_list = table_list[0].find_all("td")
    for item in td_list:
        if "采购项目名称" in item.text:
            item_name = item.text.strip().split("：")[1]
            cache_data[1] = item_name
            # print(item_name)

        if "采购项目编号" in item.text:
            item_sn = item.text.strip().split("：")[1]
            cache_data[2] = item_sn
            # print(item_sn)

        if "采购人" in item.text:
            purchaser = item.text.strip().split("：")[1].split()[0].split(",")[0]
            cache_data[3] = purchaser
            # print(purchaser)

        if "成交日期" in item.text:
            transaction_date = item.text.strip().split("：")[1]
            cache_data[4] = transaction_date
            # print(transaction_date)

        if "代理机构" in item.text:
            agency = item.text.strip().split("：")[1].split()[0]
            cache_data[5] = agency
            # print(agency)

    detail_str = "货物服务名称：%s，供应商名称：%s"
    detail = ""
    tr_list = table_list[1].find_all("tr")
    for index in range(1, len(tr_list)):
        td_list = tr_list[index].find_all("td")
        detail += detail_str % (td_list[1].text.strip(), td_list[2].text.strip()) + "\n"
        # print(detail)
    cache_data[6] = detail
    cache_data[7] = href
    return cache_data


def write_data(data_):
    print('开始写入数据 ====> ')
    # def create_csv():
    title_data = ['公告名称', '采购项目名称', '采购项目编号', '采购人', '成交日期', '代理机构', '采购详情', "链接地址"]
    with open('中标项目101-201.csv', 'w', newline='', encoding='utf-8-sig') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(title_data)
        for info in data_:
            writer.writerow(info)

    csv_file.close()


def main(page):
    # 省结果公告地址
    url = 'http://www.ccgp-shandong.gov.cn/sdgp2017/site/listnew.jsp?grade=province&colcode=0302&curpage=' + str(
        page) + '&grade=province&firstpage=1'
    print('第{}页 ====> '.format(page))
    print(url)
    # 获取所有公告链接
    announcement_html = request_data(url)
    # 解析过滤得到每一条公告的url
    href_list = parse_announcement(announcement_html)
    for href in href_list:
        # 获取公告内容
        data_html = request_data(href)
        # 解析内容
        data.append(parse_result(data_html, href))


if __name__ == "__main__":
    for i in range(101, 201):
        main(i)
        time.sleep(1)

    write_data(data)
