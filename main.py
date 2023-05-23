from classes import HeadHunter, DataBase, DBManager

hh = HeadHunter()
company_id = hh.get_request()
vacancies = hh.get_id(company_id)
db = DataBase()
db.create_database()
db.save_data_to_database(company_id, vacancies)
dbm = DBManager()
dbm.connect_to_db()
print("Sir, I've completed parsing data from the HeadHunter platform and saved all the information in the database."
      "What would you like me to do next? I can now assist you with the following tasks:")
steps = input("\n1-Show a list of companies and available positions they have "
              "\n2-Show a list of all vacancies with the company name, vacancy name, salary and a link to the vacancy"
              "\n3-Count an average salary for vacancies."
              "\n4-Show a list of all jobs that have a salary above than average salary"
              "\n5-Finding for you a list of vacancies with keyword "
              "\n(Type only number)-->")
if steps == '1':
    dbm.get_companies_and_vacancies_count()
elif steps == '2':
    dbm.get_all_vacancies()
elif steps == '3':
    dbm.get_avg_salary()
elif steps == '4':
    dbm.get_vacancies_with_higher_salary()
elif steps == '5':
    keyword = input('Type Keyword please\n-->')
    dbm.get_vacancies_with_keyword(keyword)

