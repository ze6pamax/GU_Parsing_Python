from bs4 import BeautifulSoup as bs, PageElement
import requests,re
from pprint import pprint
from pymongo import MongoClient

def create_soup(user_agent,main_link,search_params):
    if search_params:
        response = requests.get(main_link, headers=user_agent, params=search_params)
    else:
        response = requests.get(main_link, headers=user_agent)
    soup = bs(response.text, 'lxml')
    print(response.url)
    return soup

def scrapping_hh(soup):

    vacancy_block = soup.find('div',{'class':'vacancy-serp'})
    vacancy_list = vacancy_block.find_all('div',{'class':'vacancy-serp-item'})

    vacancies = []
    for vacancy in vacancy_list:
        vacancy_data = {}
        vacancy_data['title'] = vacancy.find('a',{'data-qa':'vacancy-serp__vacancy-title'}).getText()
        vacancy_data['link'] = vacancy.find('a',{'data-qa':'vacancy-serp__vacancy-title'})['href']
        salary = vacancy.find('span',{'data-qa':'vacancy-serp__vacancy-compensation'})
        if salary is None:
            vacancy_data['min_salary'] = 0
            vacancy_data['max_salary'] = 0
            vacancy_data['currency_salary'] = 0
        else:
            salary = re.split(r'[\s,-]',salary.getText().replace('\xa0',''))
            if salary[0] == 'от':
                vacancy_data['min_salary'] = int(salary[1])
                vacancy_data['max_salary'] = 0
            elif salary[0] == 'до':
                vacancy_data['min_salary'] = 0
                vacancy_data['max_salary'] = int(salary[1])
            else:
                vacancy_data['min_salary'] = int(salary[0])
                vacancy_data['max_salary'] = int(salary[1])
            vacancy_data['currency_salary'] = salary[2]
        try:
            vacancy_data['employer'] = vacancy.find('a',{'data-qa':'vacancy-serp__vacancy-employer'}).getText()
        except AttributeError:
            vacancy_data['employer'] = None
        vacancy_data['address'] = vacancy.find('span',{'data-qa':'vacancy-serp__vacancy-address'}).getText()
        vacancy_data['source'] = 'hh.ru'
        vacancies.append(vacancy_data)
    return vacancies

def add_new_vacancies(hh_res,hh_vac):

    for new_vacancy in hh_res:
        vacancy = dict(new_vacancy)
        link_check = vacancy.get('link')
        check_mongo = hh_vac.find({'link':link_check},{'link'})
        if check_mongo.count() > 0:
            continue
        else:
            hh_vac.insert_one(vacancy)

def main():

    client = MongoClient('localhost', 27017)
    db = client['vacancy_db']
    hh_vac = db.hh

    user_agent = {'User-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/83.0.4103.61 Chrome/83.0.4103.61 Safari/537.36'}

    print("Начинаем сбор с hh.ru...\n")
    # set parameters for hh:
    hh_main_link = 'https://krasnodar.hh.ru'
    #search_params = {'text':'шаурмист',
    hh_search_params = {'text':'python'}
    # write result into the file
    hh_soup = create_soup(user_agent, hh_main_link+'/search/vacancy', hh_search_params)
    hh_pager_next_flag = True
    while hh_pager_next_flag:
        hh_res = scrapping_hh(hh_soup)

        add_new_vacancies(hh_res,hh_vac)

        hh_pager_next_flag = hh_soup.find('a', {'data-qa': 'pager-next'})
        if hh_pager_next_flag:
            hh_pager_next_link = hh_soup.find('a', {'data-qa': 'pager-next'})['href']
            hh_soup = create_soup(user_agent,hh_main_link+hh_pager_next_link,None)
    print("Cбор с hh.ru окончен!\nРезультат сохранен в MongoDB в коллекцию db.hh\n")

if __name__ == "__main__":
    main()