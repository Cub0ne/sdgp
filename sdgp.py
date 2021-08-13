import requests
import re
import json
import xlwt

from bs4 import BeautifulSoup
import pandas as pd
import openpyxl


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


book = xlwt.Workbook(encoding='utf-8', style_compression=0)
sheet = book.add_sheet('采购项目', cell_overwrite_ok=True)
sheet.write(0, 0, '公告名称')
sheet.write(0, 2, '采购项目名称')
sheet.write(0, 3, '采购项目编号')
sheet.write(0, 4, '采购人')
sheet.write(0, 5, '成交日期')
sheet.write(0, 6, '代理机构')
sheet.write(0, 7, '采购详情')

# 定义存储变量
announcement_name = []
procurement_item_name = []
purchaser = []
details = []

domain = "http://www.ccgp-shandong.gov.cn"


def parse_announcement(html):
    if html is None:
        return []

    soup = BeautifulSoup(html, 'lxml')
    href_list = soup.select('a[href^="/sdgp2017/site/listcontnew.jsp?colcode=0302&"]')
    urls = []
    for href in href_list:
        print(domain + href.get('href'))
        urls.append(domain + href.get('href'))
    return urls


def parse_result(html):
    if html is None:
        return
    soup = BeautifulSoup(html, 'lxml')
    title = soup.find('h1', class_="title").text
    announcement_name.append(title)
    print(title)

    table_list = soup.find(id='textarea').find_all("table")
    td_list = table_list[0].find_all("td")
    item_name = ""
    cg = ""
    for item in td_list:
        if "采购人" in item.text:
            purchaser = item.text.strip().split("：")[1].split()[0]
            print(purchaser)
        
        if "采购项目名称" in item.text:
            item_name = item.text.strip().split("：")[1]
            print(item_name)
            
        if "采购项目编号" in item.text:
            item_sn = item.text.strip().split("：")[1]
            print(item_sn)
            
        if "成交日期" in item.text:
            item_sn = item.text.strip().split("：")[1]
            print(item_sn)
            
        if "代理机构" in item.text:
            item_sn = item.text.strip().split("：")[1].split()[0]
            print(item_sn)

        if len(cg) != 0 and len(item_name) != 0:
            break

    detail_str = "货物服务名称：%s，供应商名称：%s"
    tr_list = table_list[1].find_all("tr")
    for index in range(1, len(tr_list)):
        td_list = tr_list[index].find_all("td")
        details.append(detail_str % (td_list[1].text.strip(), td_list[2].text.strip()))
        print(detail_str % (td_list[1].text.strip(), td_list[2].text.strip()))


def write_data():
    print('开始写入数据 ====> ')
    data = pd.DataFrame.from_dict(
        {'公告名称': announcement_name, '采购项目名称': procurement_item_name, '采购人': purchaser, '采购详情': details}
        , orient='index'
    )
    writer = pd.ExcelWriter('采购.xlsx')
    data.to_excel(writer, '采购数据')
    writer.save()


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
        parse_result(data_html)

    write_data()

if __name__ == "__main__":
    for i in range(1,2):
        main(i)
    # main(1)
    # data_html = request_data("file:///C:/Users/runze/Desktop/test.html")
    # 解析内容 保存
    # parse_result(data_html)

    # book.save('项目.xls')
    # https://github.com/wistbean/learn_python3_spider
