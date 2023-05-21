from classes import HH, DBManager

vacansy = HH()
#vacansy.employers_to_db()
#vacansy.vacancies_to_db()
db =DBManager()
db.get_all_vacancies()