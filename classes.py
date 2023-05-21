import requests
import psycopg2

password = input("Please,enter your password for Database \n-->:")

class HH():
    API = "https://api.hh.ru/employers/"
    HEADERS = {
             "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0"
         }
    employers_dict = {'Yandex': '5974128', 'Sberbank': '3529', 'Tinkoff': '78638'}

    def get_request(self, employer_id) -> dict:
        params = {
            "page": 1,
            "per_page": 100,
            "employer_id": employer_id,
            "only_with_salary": True,
            "area": 113,
            "only_with_vacancies": True
        }
        return requests.get("https://api.hh.ru/vacancies/", params=params, headers=self.HEADERS).json()['items']

    def get_vacancies(self):
        vacancies_list = []
        for emp in self.employers_dict:
            emp_vacancies = self.get_request(self.employers_dict[emp])
            for vac in emp_vacancies:
                if vac['salary']['from'] is None:
                    salary = 0
                else:
                    salary = vac['salary']['from']
                vacancies_list.append({'url': vac['alternate_url'], 'salary': salary, 'vacancy_name': vac['name'], 'employer': emp})
        return vacancies_list

    def employers_to_db(self):
        with psycopg2.connect(
                host="localhost",
                database="vacancies_from_HH",
                user="postgres",
                password=password
        ) as conn:
            with conn.cursor() as cur:
                for emp in self.employers_dict:
                    cur.execute(f"INSERT INTO companies values ('{int(self.employers_dict[emp])}', '{emp}')")

    def vacancies_to_db(self):
        with psycopg2.connect(
                host="localhost",
                database="vacancies_from_HH",
                user="postgres",
                password=password
        ) as conn:
            with conn.cursor() as cur:
                for vac in self.get_vacancies():
                    cur.execute(f"INSERT INTO vacancies(vacancy_name, salary, company_name, vacancy_url) values ('{vac['vacancy_name']}', '{int(vac['salary'])}', '{vac['employer']}', '{vac['url']}')")

class DBManager():

    def get_companies_and_vacancies_count(self):
        with psycopg2.connect(
                host="localhost",
                database="vacancies_from_HH",
                user="postgres",
                password=password
        ) as conn:
            with conn.cursor() as cur:
                cur.execute('select company_name, count(vacancy_name) from vacancies_from_HH group by company_name')
                answer = cur.fetchall()
        return answer

    def get_all_vacancies(self):
        with psycopg2.connect(
                host="localhost",
                database="vacancies_from_HH",
                user="postgres",
                password=password
        ) as conn:
            with conn.cursor() as cur:
                cur.execute('select * from vacancies_from_HH')
                answer = cur.fetchall()
        return answer

    def get_avg_salary(self):
        with psycopg2.connect(
                host="localhost",
                database="vacancies_from_HH",
                user="postgres",
                password=password
        ) as conn:
            with conn.cursor() as cur:
                cur.execute('select avg(salary) from vacancies_from_HH')
                answer = cur.fetchall()
        return answer

    def get_vacancies_with_higher_salary(self):
        with psycopg2.connect(
                host="localhost",
                database="vacancies_from_HH",
                user="postgres",
                password=password
        ) as conn:
            with conn.cursor() as cur:
                cur.execute('select vacancy_name from vacancies_from_HH where salary > (select avg(salary) from vacancies_from_HH)')
                answer = cur.fetchall()
        return answer

    def get_vacancies_with_keyword(self, keyword):
        with psycopg2.connect(
                host="localhost",
                database="vacancies_from_HH",
                user="postgres",
                password=password
        ) as conn:
            with conn.cursor() as cur:
                cur.execute(f"select vacancy_name from vacancies_from_HH where vacancy_name like '%{keyword}%'")
                answer = cur.fetchall()
        return