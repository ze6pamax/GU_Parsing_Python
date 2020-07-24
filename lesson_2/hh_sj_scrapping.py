from bs4 import BeautifulSoup as bs, PageElement
import requests,re
from pprint import pprint

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
            vacancy_data['min_salary'] = None
            vacancy_data['max_salary'] = None
            vacancy_data['currency_salary'] = None
        else:
            salary = re.split(r'[\s,-]',salary.getText().replace('\xa0',''))
            if salary[0] == 'от':
                vacancy_data['min_salary'] = salary[1]
                vacancy_data['max_salary'] = None
            elif salary[0] == 'до':
                vacancy_data['min_salary'] = None
                vacancy_data['max_salary'] = salary[1]
            else:
                vacancy_data['min_salary'] = salary[0]
                vacancy_data['max_salary'] = salary[1]
            vacancy_data['currency_salary'] = salary[2]
        try:
            vacancy_data['employer'] = vacancy.find('a',{'data-qa':'vacancy-serp__vacancy-employer'}).getText()
        except AttributeError:
            vacancy_data['employer'] = None
        vacancy_data['address'] = vacancy.find('span',{'data-qa':'vacancy-serp__vacancy-address'}).getText()
        vacancy_data['source'] = 'hh.ru'
        vacancies.append(vacancy_data)
    return vacancies

def scrapping_sj(soup):

    vacancy_block = soup.find('div', {'class': '_1ID8B'})
    vacancy_list = vacancy_block.find_all('div', {'class': '_3zucV _1fMKr undefined _1NAsu'})

    vacancies = []
    for vacancy in vacancy_list:
        vacancy_data = {}
        title = vacancy.find('a',{})
        if title:
            vacancy_data['title'] = title.getText()
        else:
            vacancy_data['title'] = None
        link = vacancy.find('a',{})
        if link:
            vacancy_data['link'] = link['href']
        else:
            vacancy_data['link'] = None
        salary = vacancy.find('span',{'class':'_3mfro _2Wp8I PlM3e _2JVkc _2VHxz'})
        if salary:
            vacancy_data['salary'] = salary.getText()
        else:
            vacancy_data['salary'] = None
        employer = vacancy.find('span', {'class': '_3mfro _3Fsn4 f-test-text-vacancy-item-company-name _9fXTd _2JVkc _2VHxz _15msI'})
        if employer:
            vacancy_data['employer'] = employer.findChild().getText()
        else:
            vacancy_data['employer'] = None
        address = vacancy.find('span',{'class':'clLH5'})
        if address:
            vacancy_data['address'] = address.findNextSibling().getText()
        else:
            vacancy_data['address'] = None
        vacancy_data['source'] = 'superjob.ru'
        vacancies.append(vacancy_data)
    return vacancies

def main():

    user_agent = {'User-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/83.0.4103.61 Chrome/83.0.4103.61 Safari/537.36'}

    print("Начинаем сбор с hh.ru...\n")

    # set parameters for hh:
    hh_main_link = 'https://krasnodar.hh.ru'
    #search_params = {'text':'шаурмист',
    hh_search_params = {'text':'python',
                    'search_field':'name',
                     'area':'113'}
    # write result into the file
    with open('/home/zebramax/hh_vacancy_list.csv','w') as f:
        hh_soup = create_soup(user_agent, hh_main_link+'/search/vacancy', hh_search_params)
        hh_pager_next_flag = True
        while hh_pager_next_flag:
            hh_res = scrapping_hh(hh_soup)
            f.write(str(hh_res))
            hh_pager_next_flag = hh_soup.find('a', {'data-qa': 'pager-next'})
            if hh_pager_next_flag:
                hh_pager_next_link = hh_soup.find('a', {'data-qa': 'pager-next'})['href']
                hh_soup = create_soup(user_agent,hh_main_link+hh_pager_next_link,None)
    print("Cбор с hh.ru окончен!\nРезультат сохранен в файл hh_vacancy_list.csv\n")
    print("Начинаем сбор с superjob.ru...\n")
    # set parameters for sj:
    sj_main_link = 'https://russia.superjob.ru'
    sj_search_params = {'keywords': 'python'}
    with open('/home/zebramax/sj_vacancy_list.csv', 'w') as f:
        sj_soup = create_soup(user_agent, sj_main_link + '/vacancy/search', sj_search_params)
        sj_pager_next_flag = True
        while sj_pager_next_flag:
            sj_res = scrapping_sj(sj_soup)
            f.write(str(sj_res))
            sj_pager_next_flag = sj_soup.find('a',{'rel':'next'})
            if sj_pager_next_flag:
                sj_pager_next_link = sj_pager_next_flag['href']
                sj_soup = create_soup(user_agent,sj_main_link+sj_pager_next_link,None)
    print("Cбор с superjob.ru окончен!\nРезультат сохранен в файл sj_vacancy_list.csv.")
if __name__ == "__main__":
    main()