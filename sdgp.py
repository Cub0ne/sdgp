import time
import requests
from bs4 import BeautifulSoup
import pymysql


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


domain = "http://www.ccgp-shandong.gov.cn"


def parse_announcement(html):
    if html is None:
        return []

    soup = BeautifulSoup(html, 'lxml')
    href_list = soup.select('a[href^="/sdgp2017/site/listcontnew.jsp?colcode=0302&"]')
    urls = []
    for href in href_list:
        urls.append(domain + href.get('href'))
    return urls


def parse_result(html):
    cache_data = ['', '', '', '', '', '', '']
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
            cache_data[1] = item.text.strip().split("：")[1]

        if "采购项目编号" in item.text:
            cache_data[2] = item.text.strip().split("：")[1]

        if "采购人" in item.text:
            cache_data[3] = item.text.strip().split("：")[1].split()[0].split(",")[0]

        if "成交日期" in item.text:
            cache_data[4] = item.text.strip().split("：")[1]

        if "代理机构" in item.text:
            cache_data[5] = item.text.strip().split("：")[1].split()[0]

    detail_str = "货物服务名称：%s，供应商名称：%s"
    detail = ""
    tr_list = table_list[1].find_all("tr")
    for index in range(1, len(tr_list)):
        td_list = tr_list[index].find_all("td")
        detail += detail_str % (td_list[1].text.strip(), td_list[2].text.strip()) + "\n"
    cache_data[6] = detail
    return cache_data


def add_new(page, db):
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
        data = parse_result(data_html)

        # SQL 插入语句
        sql = """INSERT INTO ccgp(announcement_name,prj_name, prj_sn, purchaser, deal_date,agency,detail,href)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        param = (data[0], data[1], data[2], data[3], data[4], data[5], data[6], href)
        print(param)
        try:
            with db.cursor() as cursor:
                if cursor.execute(sql, param) == 1:
                    print('insert successful')
        except pymysql.MySQLError as error:
            print('insert fail')
            print(error)
            # 如果发生错误则回滚
            db.rollback()


def main():
    # 打开数据库连接
    db = pymysql.connect(host='146.56.178.192', port=6033,
                         user='root', passwd='svend123',
                         db='ccgp', charset='utf8mb4',
                         autocommit=True,
                         cursorclass=pymysql.cursors.DictCursor)
    for i in range(11, 31):
        add_new(i, db)
        time.sleep(1)
    # 关闭数据库连接
    db.close()


if __name__ == "__main__":
    main()
