import psycopg2
import requests


class HeadHunter:
    """Данный класс создает запрос на API hh.ru"""

    def get_request(self):
        """Данный метод делай запрос по api и берет id компаний"""

        company_list = []
        employers_list = ['Яндекс', 'Альфа-Банк',  # Список 10 компаний для работы
                          'VK', 'IBS', 'Авито ',
                          'Т1', '1С',
                          'Лаборатория Касперского', 'Тензор',
                          'Билайн']
        for item in employers_list:
            request = requests.get("https://api.hh.ru/employers",
                                   params={
                                       'text': item,  # Названия компании(Работодателя)
                                       'per_page': 1,  # Количество компаний
                                       'area': 113,  # Регион Российской Федерации
                                       'only_with_vacancies': 'true'  # Запрос только с вакансиями
                                   }
                                   ).json()['items']
            for item2 in request:
                company_list.append(item2)
        return company_list

    def get_id(self, id) -> list[dict]:
        """Используя id компаний этом метод выводит список всех вакансий"""
        vacancy_list = []
        for item in id:
            for i in range(5):
                request = requests.get(f'https://api.hh.ru/vacancies?employer_id={item["id"]}',
                                       params={'page': i, 'per_page': 10}).json()['items']
                for req in request:
                    vacancy_list.append(req)
        return vacancy_list


db_password = input("Please,enter your password for Database \n-->:")


class DataBase:
    """Данный класс используя запрос из hh загружает данные в Базу Данных """

    def create_database(self):

        """Создание базы данных и таблиц для сохранения данных."""
        conn = psycopg2.connect(host='Localhost', database='Test', user='postgres',
                                password=db_password)
        conn.autocommit = True
        cur = conn.cursor()

        try:
            # команда для создания базы данных
            sql = "CREATE DATABASE hh_database"
            drop_sql = "DROP DATABASE hh_database"
            # выполняем код sql
            cur.execute(sql)
        except psycopg2.errors.DuplicateDatabase:
            cur.execute(drop_sql)
            cur.execute(sql)
            print('Database has been recreated successfully')
        else:
            print("Database created successfully")

        cur.close()
        conn.close()

        conn = psycopg2.connect(host='Localhost', database='hh_database', user='postgres',
                                password=db_password)

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

        conn = psycopg2.connect(host='Localhost', database='hh_database', user='postgres',
                                password=input("Please,enter your password for Database \n-->:"))

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


class DBManager:
    """Класс подключаться к БД Postgres для вывода информации """

    def connect_to_db(self):
        """Формирует запрос в Базе Данных"""
        conn = psycopg2.connect(host='Localhost', database='HH_database', user='postgres',
                                password=input("Please,enter your password for Database \n-->:"))
        return conn

    def get_companies_and_vacancies_count(self) -> None:
        """Получает список всех компаний и количество вакансий у каждой компании."""
        conn = self.connect_to_db()
        with conn.cursor() as cur:
            cur.execute("SELECT company_name, company_open_vacansies FROM company")
            rows = cur.fetchall()
            for row in rows:
                print(row)

        conn.commit()
        conn.close()

    def get_all_vacancies(self) -> None:
        """Получает список всех вакансий с указанием названия компании, названия вакансии и зарплаты и ссылки на вакансию"""
        conn = self.connect_to_db()
        with conn.cursor() as cur:
            cur.execute("""SELECT vacancies, company_name, salary, url_vacancy
                        FROM vacancy
                        JOIN company USING(company_id)""")
            rows = cur.fetchall()
            for row in rows:
                print(row)

        conn.commit()
        conn.close()

    def get_avg_salary(self) -> None:
        """Получает среднюю зарплату по вакансиям."""
        conn = self.connect_to_db()
        with conn.cursor() as cur:
            cur.execute("""SELECT ROUND(AVG(salary), 2) FROM vacancy
                           WHERE salary NOT IN ('0')""")
            rows = cur.fetchall()
            for row in rows:
                print(row)

        conn.commit()
        conn.close()

    def get_vacancies_with_higher_salary(self) -> None:
        """Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям."""
        conn = self.connect_to_db()
        with conn.cursor() as cur:
            cur.execute("""SELECT company_name, vacancies, salary, url_vacancy  
                            FROM vacancy
                            JOIN company USING(company_id)
                           WHERE salary > (SELECT AVG(salary) FROM vacancy WHERE salary != 0)""")
            rows = cur.fetchall()
            for row in rows:
                print(row)

        conn.commit()
        conn.close()

    def get_vacancies_with_keyword(self, word) -> None:
        """Получает список всех вакансий, в названии которых содержатся переданные в метод слова"""
        conn = self.connect_to_db()
        with conn.cursor() as cur:
            cur.execute(f"""SELECT company_name, vacancies, salary, url_vacancy  
                            FROM vacancy
                            JOIN company USING(company_id)
                            WHERE vacancies LIKE '%{word.capitalize()}%'""")
            rows = cur.fetchall()
            for row in rows:
                print(row)
        conn.commit()
        conn.close()
