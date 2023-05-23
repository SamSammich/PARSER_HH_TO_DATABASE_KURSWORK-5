import psycopg2
import requests

db_password = input("Greetings, Sir! I am Jarvis, your trusted job search assistant for today."
                    "\n Sir, Please,enter your password for Database \n-->:")




class HeadHunter:
    """Creating Class HeadHunter"""

    def get_request(self):
        """Getting company IDs"""

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
        """Using ID getting all vacancies"""
        vacancy_list = []
        for item in id:
            for i in range(5):
                request = requests.get(f'https://api.hh.ru/vacancies?employer_id={item["id"]}',
                                       params={'page': i, 'per_page': 10}).json()['items']
                for req in request:
                    vacancy_list.append(req)
        return vacancy_list





class DataBase:
    """This class creating Database and filling it"""

    def create_database(self):

        """Creating Database and Tables."""
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
            print('Sir, its Jarvis. The database has been successfully recreated.')
        else:
            print("Sir, Database created successfully")

        cur.close()
        conn.close()

        conn = psycopg2.connect(host='Localhost', database='hh_database', user='postgres',
                                password=db_password)

        with conn.cursor() as cur:
            cur.execute("""
                   CREATE TABLE company (
                       company_id INTEGER,
                       company_name VARCHAR(255) NOT NULL,
                       company_open_vacancies INTEGER
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
        """Saving data to Database."""

        conn = psycopg2.connect(host='Localhost', database='hh_database', user='postgres',
                                password=db_password)

        with conn.cursor() as cur:
            for company in companies:
                company_id = company['id']
                company_name = company['name']
                company_vacancies = company['open_vacancies']
                cur.execute(
                    """
                    INSERT INTO company(company_id, company_name, company_open_vacancies)
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
    """This class links to the Database and handles information."""

    def connect_to_db(self):
        """Connecting to Database"""
        conn = psycopg2.connect(host='Localhost', database='hh_database', user='postgres',
                                password=db_password)
        return conn

    def get_companies_and_vacancies_count(self) -> None:
        """Getting a list of companies and available positions they have """
        conn = self.connect_to_db()
        with conn.cursor() as cur:
            cur.execute("SELECT company_name, company_open_vacancies FROM company")
            rows = cur.fetchall()
            for row in rows:
                print(row)

        conn.commit()
        conn.close()

    def get_all_vacancies(self) -> None:
        """Getting a list of all vacancies with the company name, vacancy name, salary and a link to the vacancy"""
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
        """Getting an average salary for vacancies."""
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
        """Getting a list of all jobs that have a salary above than average salary"""
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
        """Getting a list of vacancies with keyword"""
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
