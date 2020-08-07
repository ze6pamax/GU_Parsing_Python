from lxml import html
import requests
import time
from datetime import date
from pymongo import MongoClient


def get_dom(main_link, header):
    response = requests.get(main_link, headers=header)
    return html.fromstring(response.text)


def mail_news_parser(dom, main_link):
    """
    Вытаскиваем разные ссылки на разные виды новостей
    """
    link_main_news = dom.xpath("//div[@class='daynews__item daynews__item_big']/a/@href")
    link_daynews_list = dom.xpath("//div[@class='daynews__item']/a/@href")
    link_list_items = dom.xpath("//li[@class='list__item']/a/@href")
    link_newsitems_big = dom.xpath("//a[@class='newsitem__title link-holder']/@href") # не надо лепить news.mail.ru
    """
    Собираем ссылки в один список
    """
    links = [link if link.startswith("http") else main_link+link
             for link in link_main_news + link_daynews_list + link_list_items + link_newsitems_big]
    """
    Складываем данные в словарь
    """
    news_block = []

    for link in links:
        time.sleep(0.3)

        news = {}

        link_response = requests.get(link,headers=headers)
        dom = html.fromstring(link_response.text)

        title = dom.xpath("//h1[@class='hdr__inner']/text()")
        source = dom.xpath("//a[@class='link color_gray breadcrumbs__link']/@href")
        publish_time = dom.xpath("//span[@class='note__text breadcrumbs__text js-ago']/text()")
        publish_date = date.today()

        news['link'] = link
        news['title'] = "|".join(title)
        news['source'] = "|".join(source)
        news['publish_time'] = "|".join(publish_time)
        news['publish_date'] = publish_date.strftime("%Y-%m-%d")

        news_block.append(news)
    return news_block


def yandex_news_parser(dom, main_link):
    news_block = []

    news_list = dom.xpath("//div[contains(@class,'mg-grid__row mg-grid__row_gap_8 news')]//div[contains(@class,'mg-grid__col mg-grid__col_xs')]//article")
    link_to_complete_url = main_link.replace('/news','')
    for link in news_list:
        time.sleep(0.3)
        news = {}
        news_link = link.xpath(".//a[@class='news-card__link']/@href")
        title = link.xpath(".//h2[@class='news-card__title']/text()")
        source = link.xpath(".//span/a/text()")
        publish_time = link.xpath(".//span[@class='mg-card-source__time']/text()")
        publish_date = date.today()

        news['link'] = f'{link_to_complete_url}{news_link[0]}'
        news['title'] = title[0]
        news['source'] = source[0]
        news['publish_time'] = publish_time[0]
        news['publish_date'] = publish_date.strftime("%Y-%m-%d")

        news_block.append(news)
    return news_block


def lenta_news_parser(dom, main_link):
    news_block = []

    main_news = dom.xpath("//div[@class='span8 js-main__content']//div[@class='span4']/div[contains(@class,'item')]")
    news_with_picture = dom.xpath("//div[@class='span4']//div[@class='item article']")
    other_news = dom.xpath("//div[@class='span4']//div[@class='item news b-tabloid__topic_news']")

    for link in main_news:
        time.sleep(0.3)
        news = {}

        news_link = link.xpath(".//a/@href")
        if link.xpath(".//h2/a/text()"):
            title = link.xpath(".//h2/a/text()")
            publish_time = link.xpath(".//h2/a/time/text()")
        else:
            title = link.xpath(".//a/text()")
            publish_time = link.xpath(".//a/time/text()")
        publish_date = date.today()

        news['link'] = main_link+news_link[0]
        news['title'] = title[0]
        news['source'] = main_link
        news['publish_time'] = publish_time[0]
        news['publish_date'] = publish_date.strftime("%Y-%m-%d")

        news_block.append(news)

    for link in news_with_picture:
        time.sleep(0.3)
        news = {}

        news_link = link.xpath(".//h3/a/@href")
        title = link.xpath(".//a/span/text()")
        publish_time = link.xpath(".//span[@class='time']/text()")
        publish_date = date.today()
        for sub_string in news_link:
            if 'http' in sub_string:
                news['link'] = news_link[0]
            else:
                news['link'] = main_link + news_link[0]
        news['title'] = title[0]
        news['source'] = main_link
        news['publish_time'] = publish_time
        news['publish_date'] = publish_date.strftime("%Y-%m-%d")

        news_block.append(news)

    for link in other_news:
        time.sleep(0.3)
        news = {}

        news_link = link.xpath(".//h3/a/@href")
        title = link.xpath(".//a/span/text()")
        publish_time = link.xpath(".//span[@class='time']/text()")
        publish_date = date.today()

        for sub_string in news_link:
            if 'http' in sub_string:
                news['link'] = news_link[0]
            else:
                news['link'] = main_link + news_link[0]
        news['title'] = title[0]
        news['source'] = main_link
        news['publish_time'] = publish_time[0]
        news['publish_date'] = publish_date.strftime("%Y-%m-%d")

        news_block.append(news)

    return news_block


def mongo_connection(news_block):
    client = MongoClient('localhost', 27017)
    db = client['news_db']

    news_collection = db.news_collection

    news_collection.insert_one(news_block)


headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
           'Cookie' : 'VID=0tG7g40EXP1y00000R0sD4Hy:::0-0-0-445445c:CAASEAi4GfQT0Fg9sLS4uaSDILQaYA42a4cK7mY7xdJsy8m7NNmO0eYKW1YeC-q7UiPIoQxwBxoRKWOVjCzCWTlQyTnWno6SHsj-gmZfkfGrTvGqUsOq0AGNAxY6qtpo0y_uoiv-m83ppvkcTTxETA0l6SrmQg'}
mail_link = 'https://news.mail.ru'
yandex_link = 'https://yandex.ru/news'
lenta_link = 'https://lenta.ru'

def main():

    total_news_block = []

    mail_dom = get_dom(mail_link, headers)
    mail_news_block = mail_news_parser(mail_dom, mail_link)
    yandex_dom = get_dom(yandex_link, headers)
    yandex_news_block = yandex_news_parser(yandex_dom, yandex_link)
    lenta_dom = get_dom(lenta_link, headers)
    lenta_news_block = lenta_news_parser(lenta_dom, lenta_link)

    total_news_block = mail_news_block + yandex_news_block + lenta_news_block

    for news in total_news_block:
        mongo_connection(news)

if __name__ == "__main__":
    main()


