import psycopg2
import requests
from config import config
from pprint import pprint


class HeadHunter:
    """Данный класс создает запрос на API hh.ru"""

    def get_request(self) -> list[dict]:
        """Данный метод делай запрос по api и берет id компаний"""

        company_list = []
        employers_list = ['Ростех', 'OCS Distribution',  # Список 10 компаний для работы
                          'Softline', 'IBS', 'Afterlogic ',
                          'Т1', '1С',
                          'Лаборатория Касперского', '3Logic Group',
                          'Айтеко']
        for item in employers_list:
            request = requests.get("https://api.hh.ru/employers",
                                   params={
                                       'text': item,  # Названия компании(Работодателя)
                                       'per_page': 1,  # Количество компаний
                                       'area': 113,  # Регион Российской Федерации
                                       'only_with_vacancies': 'true'  # Запрос только с ваканииями
                                   }
                                   ).json()['items']
            for item2 in request:
                company_list.append(item2)
        return company_list

    def get_id(self, id) -> list[dict]:
        """Используя id компаний этом метод выводит список всех вакансий"""
        vacancy_list = []
        for item in id:
            for item2 in range(5):
                request = requests.get(f'https://api.hh.ru/vacancies?employer_id={item["id"]}',
                                       params={'page': item2, 'per_page': 100}).json()['items']
                for item3 in request:
                    vacancy_list.append(item3)
        return vacancy_list


class DataBase:
    """Данный класс используя запрос из hh загружает данные в Базу Данных """
    def __init__(self):
        self.config = config()


    def create_database(self):
        """Создание базы данных и таблиц для сохранения данных."""

        conn = psycopg2.connect(dbname='postgres', **self.config)
        conn.autocommit = True
        cur = conn.cursor()

        cur.execute("DROP DATABASE course_work")
        cur.execute("CREATE DATABASE course_work")

        cur.close()
        conn.close()

        conn = psycopg2.connect(dbname='course_work', **self.config)

        with conn.cursor() as cur:
            cur.execute("""
                   CREATE TABLE company (
                       company_id INTEGER,
                       company_name VARCHAR(255) NOT NULL,
                       company_open_vacansies INTEGER
                   )
               """)

        with conn.cursor() as cur:
            cur.execute("""
                   CREATE TABLE vacancy (
                       company_id INTEGER,
                       vacancies VARCHAR(255) NOT NULL,
                       salary INTEGER,
                       url_vacancy TEXT
                   )
               """)
        conn.commit()
        conn.close()

    def save_data_to_database(self, companies, vacancies):
        """Сохранение данных в таблицы."""

        conn = psycopg2.connect(dbname='course_work', **self.config)

        with conn.cursor() as cur:
            for company in companies:
                company_id = company['id']
                company_name = company['name']
                company_vacancies = company['open_vacancies']
                cur.execute(
                    """
                    INSERT INTO company(company_id, company_name, company_open_vacansies)
                    VALUES (%s, %s, %s)
                    """,
                    (company_id, company_name, company_vacancies)
                )
                for vacancy in vacancies:
                    id = vacancy['employer']['id']
                    vacancy_name = vacancy['name']
                    url_vacancy = vacancy['alternate_url']
                    salary = vacancy['salary']
                    if salary is not None:
                        if salary.get('from') is None:
                            salary = salary['to']
                        else:
                            salary = salary['from']
                    else:
                        salary = 0
                    cur.execute(
                        """
                        INSERT INTO vacancy(company_id, vacancies, salary, url_vacancy)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (id, vacancy_name, salary, url_vacancy)
                    )
        conn.commit()
        conn.close()