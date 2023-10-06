import datetime
import random
import time

import requests
from bs4 import BeautifulSoup as bs

__all__ = ('work_ua', 'rabota_ua', 'dou', 'djinni')

user_agents = [
    # User Agents for Browsers on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.1234.5678 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.1234.5678 Safari/537.36 Edg/100.0",
    "Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.1234.5678 Safari/537.36 OPR/100.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
]

headers = {
    'User-Agent': random.choice(user_agents),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate'}


def work_ua(search, location=None):
    search_id = search.id
    if location:
        search = location.slug + '-' + search.slug.replace(' ', '-')
    else:
        search = search.slug.replace(' ', '-')
    page_number = 1
    search_url = f"https://www.work.ua/jobs-{search}/?page={page_number}"
    jobs = []
    errors = []
    while True:
        response = requests.get(search_url, headers=headers)
        if response.status_code == 200:
            soup = bs(response.content, 'html.parser')
            job_div = soup.find('div', id='pjax-job-list')
            if job_div:
                jobs_list = job_div.find_all('div', attrs={'class': 'card card-hover card-visited wordwrap job-link'})
                for i in jobs_list:
                    job_name = i.find('a', attrs={'href': lambda href: href and href.startswith('/jobs/')}).text
                    job_description = i.find('p', attrs={'class': 'overflow text-muted add-top-sm cut-bottom'}).text
                    job_company = i.find('div', attrs={'class': 'add-top-xs'}).find_next('b').text
                    job_link = i.find('a', attrs={'href': lambda href: href and href.startswith('/jobs/')}).get('href')
                    job_payment = i.find('b').text
                    job_payment = job_payment if job_payment[:1].isdigit() else '$No info'
                    # job_time = datetime.date.today().strftime("%d %B %Y")
                    if location is not None:
                        jobs.append({'title': job_name, 'description': job_description, 'company': job_company,
                                     'url': f"https://www.work.ua{job_link}", 'salary': job_payment,
                                     'search_id': search_id, 'location_id': location.id})
                    else:
                        jobs.append({'title': job_name, 'description': job_description, 'company': job_company,
                                     'url': f"https://www.work.ua{job_link}", 'salary': job_payment,
                                     'search_id': search_id})
                page_number += 1
                search_url = search_url.replace(search_url[-1], f"{page_number}")
            else:
                errors.append({'url': search_url, 'title': "Div does not exists"})
                break
        else:
            errors.append({'url': search_url, 'title': f'Page do not response, code:{response.status_code}'})
            return errors
    return jobs, errors


def rabota_ua(search, location=None):
    url = "https://dracula.robota.ua/?q=getPublishedVacanciesList"
    city_url = "https://ua-api.robota.ua/dictionary/city"
    city = requests.get(city_url).json()
    found_id = None
    if location is not None:
        for obj in city:
            if obj.get("en") == location.slug:
                found_id = obj.get("id")
                break
    graphql_query = """
    query getPublishedVacanciesList($filter: PublishedVacanciesFilterInput!, $pagination: PublishedVacanciesPaginationInput!, $sort: PublishedVacanciesSortType!) {
      publishedVacancies(filter: $filter, pagination: $pagination, sort: $sort) {
        totalCount
        items {
          id
          title
          description
          sortDate
          salary {
            amount
            comment
            amountFrom
            amountTo
          }
          company {
            id
            name
          }
          city {
            name
          }
          isActive
        }
      }
    }
    """
    page_number = 0
    # Send a GET request to the URL
    jobs, errors = [], []
    while True:
        variables = {
            "filter": {
                "keywords": f"{search.slug}",
                "clusterKeywords": [],
                "salary": 0,
                "districtIds": [],
                "scheduleIds": [],
                "rubrics": [],
                "metroBranches": [],
                "showAgencies": True,
                "showOnlyNoCvApplyVacancies": False,
                "showOnlySpecialNeeds": False,
                "showOnlyWithoutExperience": False,
                "showOnlyNotViewed": False,
                "showWithoutSalary": True
            },
            "pagination": {
                "count": 40,
                "page": page_number
            },
            "sort": "BY_DATE"
        }
        if found_id is not None:
            variables['filter']['cityId'] = str(found_id)
        response = requests.post(url, json={"query": graphql_query, "variables": variables})
        for i in response.json()['data']['publishedVacancies']['items']:
            salary = f"{i['salary']['amountFrom']}-{i['salary']['amountTo']}" if i['salary']['amountFrom'] and \
                                                                                 i['salary']['amountTo'] != 0 else \
            i['salary']['amount'] if i['salary']['amount'] != 0 else '$No info'
            if location is not None:
                    try:
                        jobs.append(
                        {'title': i['title'], 'description': i['description'], 'company': i['company']['name'],
                         'url': f"https://robota.ua/company{i['company']['id'].replace(' ', '')}/vacancy{i['id'].replace(' ', '')}",
                         'salary': salary, 'search_id': search.id, 'location_id': location.id})
                    except:
                        pass
            else:
                try:
                    jobs.append(
                    {'title': i['title'], 'description': i['description'], 'company': i['company']['name'],
                     'url': f"https://robota.ua/company{i['company']['id'].replace(' ', '')}/vacancy{i['id'].replace(' ', '')}",
                     'salary': salary, 'search_id': search.id})
                except:
                    pass
        page_number += 1
        if len(response.json()['data']['publishedVacancies']['items']) < 1:
            break
    return jobs, errors


def dou(search, location=None):
    search_id = search.id
    search = search.slug.replace(' ', '+')
    link = f'https://jobs.dou.ua/vacancies/?search={search}'
    if location is not None:
        link = f'https://jobs.dou.ua/vacancies/?search={search}&city={location.slug}'
    response = requests.get(link, headers=headers)
    errors = []
    if response.status_code == 200:
        soup = bs(response.content, 'html.parser')
        job_div = soup.find_all('li', attrs={'class': 'l-vacancy'})
        jobs = []
        for i in job_div:
            job_name = i.find('a', attrs={'class': 'vt'}).text
            job_description = i.find('div', attrs={'class': 'sh-info'}).text
            job_company = i.find('a', attrs={'class': 'company'}).text
            job_link = i.find('a', attrs={'class': 'vt'}).get('href')
            # try:
            #     job_time = i.find('div', attrs={'class': 'date'}).text
            # except AttributeError:
            #     job_time = datetime.date.today().strftime("%d %B %Y")
            try:
                job_payment = i.find('span', attrs={'class': 'salary'}).text
            except AttributeError:
                job_payment = '$No info'
            if location is not None:
                jobs.append({'title': job_name, 'description': job_description, 'company': job_company,
                         'url': job_link, 'salary': job_payment, 'search_id': search_id, 'location_id': location.id})
            else:
                jobs.append({'title': job_name, 'description': job_description, 'company': job_company,
                         'url': job_link, 'salary': job_payment, 'search_id': search_id})
        scroll_down_link = f'https://jobs.dou.ua/vacancies/xhr-load/?search={search}'
        csrf_token = response.cookies.get('csrftoken')
        csrfmiddleware_token = soup.find('input', {'name': 'csrfmiddlewaretoken'}).get('value')
        internal_headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Length': '93',
            'Origin': 'https://jobs.dou.ua',
            'Connection': 'keep-alive',
            'Referer': link,
            'Cookie': f'csrftoken={csrf_token}',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin'
        }
        count = 20
        while True:
            data = {'csrfmiddlewaretoken': csrfmiddleware_token,
                    'count': count}
            response = requests.post(scroll_down_link, headers=internal_headers, data=data, cookies=response.cookies)
            soup = (bs(response.json()['html'], 'html.parser'))
            job_divs = soup.findAll('li', attrs={'class': 'l-vacancy'})
            for i in job_divs:
                job_name = i.find('a', attrs={'class': 'vt'}).text
                job_description = i.find('div', attrs={'class': 'sh-info'}).text
                job_company = i.find('a', attrs={'class': 'company'}).text
                job_link = i.find('a', attrs={'class': 'vt'}).get('href')
                try:
                    job_time = i.find('div', attrs={'class': 'date'}).text
                except AttributeError:
                    job_time = datetime.date.today().strftime("%d %B %Y")
                try:
                    job_payment = i.find('span', attrs={'class': 'salary'}).text
                except AttributeError:
                    job_payment = '$No info'
                if location is not None:
                    jobs.append({'title': job_name, 'description': job_description, 'company': job_company,
                                 'url': job_link, 'salary': job_payment, 'search_id': search_id,
                                 'location_id': location.id})
                else:
                    jobs.append({'title': job_name, 'description': job_description, 'company': job_company,
                                 'url': job_link, 'salary': job_payment, 'search_id': search_id})
            if response.json()['last']:
                break
            else:
                count += response.json()['num']
        return jobs, errors
    else:
        errors.append({'url': link, 'title': f'Page do not response, code:{response.status_code}'})
        time.sleep(10)
        return errors


def djinni(search, location=None):
    jobs, errors = [], []
    page = 1
    while True:
        search_link = f'https://djinni.co/jobs/?all-keywords={search.slug}&any-of-keywords=&exclude-keywords=&keywords={search.slug}&page={page}'
        if location is not None:
            search_link = f'https://djinni.co/jobs/?all-keywords={search.slug}&any-of-keywords=&exclude-keywords=&keywords={search.slug}&location={location.slug}&page={page}'
        response = requests.get(search_link)
        if response.status_code == 200:
            soup = bs(response.content, 'html.parser')
            jobs_list = soup.find_all('li', attrs={'class': 'list-jobs__item job-list__item'})
            for i in jobs_list:
                job_name = i.find('a', attrs={'class': 'h3 job-list-item__link'}).text
                job_company = i.find('a', attrs={'class': 'mr-2'}).text
                job_link = i.find('a', attrs={'class': 'h3 job-list-item__link'}).get('href')
                job_description = i.find('div', attrs={'class': 'job-list-item__description'}).text
                try:
                    job_payment = i.find('span', attrs={'class': 'public-salary-item'}).text
                except AttributeError:
                    job_payment = "$No info"
                # job_time = i.find('span', {'class': 'mr-2 nobr'}).get('data-original-title')
                if location is not None:
                    jobs.append({'title': job_name, 'description': job_description, 'company': job_company,
                                 'url': f"https://djinni.co{job_link}", 'salary': job_payment, 'search_id': search.id,
                                 'location_id': location.id})
                else:
                    jobs.append({'title': job_name, 'description': job_description, 'company': job_company,
                                 'url': f"https://djinni.co{job_link}", 'salary': job_payment, 'search_id': search.id})
            if search.slug not in soup.find('header', attrs={'class': 'page-header'}).text:
                break
            page += 1
        else:
            errors.append({'url': search_link, 'title': f'Page do not response, code:{response.status_code}'})
    return jobs, errors
