import requests
import re
import json
import xlwt

from bs4 import BeautifulSoup


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
sheet.write(0, 0, '序号')
sheet.write(0, 1, '供应商名称')
sheet.write(0, 2, '采购项目名称')
sheet.write(0, 3, '采购人')
n = 1
item_name = ""
purchaser = ""

domain = "http://www.ccgp-shandong.gov.cn"


def parse_announcement(html):
    if len(html) < 0:
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
    textarea = soup.find(id='textarea')
    # print(textarea.text)
    title = soup.find('h1', class_="title").text
    print(title)
    if "山东正中信息技术股份有限公司" in textarea.text:
        print(title + "=====> 山东正中信息技术股份有限公司")
        table = textarea.find_all("td")
        for item in table:
            if "采购项目名称" in item.text:
                global item_name
                item_name = item.text
                print("采购项目名称" + item_name)

            if "采购人" in item.text:
                global purchaser
                purchaser = item.text
                print("采购人" + purchaser)

        global n
        sheet.write(n, 0, n)
        sheet.write(n, 1, "山东正中信息技术股份有限公司")
        sheet.write(n, 2, item_name)
        sheet.write(n, 3, purchaser)
        n = n + 1

    else:
        print("==================================")


def write_data(item):
    print('开始写入数据 ====> ' + str(item))

    # with open('book.txt', 'a', encoding='UTF-8') as f:
    #     f.write(json.dumps(item, ensure_ascii=False) + '\n')


def main(page):
    # 省结果公告地址
    url = 'http://www.ccgp-shandong.gov.cn/sdgp2017/site/listnew.jsp?grade=province&colcode=0302&curpage=' + str(
        page) + '&grade=province&firstpage=1'
    print('第{}页 ====> '.format(page))
    print(url)
    # 获取所有公告
    announcement_html = request_data(url)
    # 解析过滤得到每一条公告的url
    href_list = parse_announcement(announcement_html)
    for href in href_list:
        data_html = request_data(href)
        parse_result(data_html)


if __name__ == "__main__":
    for i in range(100, 150):
        main(i)
    # main(1)
    book.save('项目.xls')
    # https://github.com/wistbean/learn_python3_spider
    # request_dandan("http://www.ccgp-shandong.gov.cn/sdgp2017/site/listcontnew.jsp?colcode=0302&id=203715338")
