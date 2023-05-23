-- Creating Database
CREATE DATABASE hh_database;

-- Creating Table company
CREATE TABLE company
(
    company_id             INTEGER,
    company_name           VARCHAR(255) NOT NULL,
    company_open_vacancies INTEGER
);

-- Creating Table vacancy
CREATE TABLE vacancy
(
    company_id  INTEGER,
    vacancies   VARCHAR(255) NOT NULL,
    salary      INTEGER,
    url_vacancy TEXT
);

-- filling table with columns
INSERT INTO company(company_id, company_name, company_open_vacancies)
VALUES (%s, %s, %s);

INSERT INTO vacancy(company_id, vacancies, salary, url_vacancy)
VALUES (%s, %s, %s, %s);

--Getting list of all companies and the number of vacancies for each company..
SELECT company_name, company_open_vacancies FROM company;

--Getting list of all vacancies with the company name, vacancy name, salary and link
SELECT vacancies, company_name, salary, url_vacancy
FROM vacancy
JOIN company USING(company_id);

--Getting an average salary for vacancies.
SELECT ROUND(AVG(salary), 2) FROM vacancy
WHERE salary NOT IN ('0');

--Getting list of all vacancies that have a salary higher than the average salary
SELECT company_name, vacancies, salary, url_vacancy
FROM vacancy
JOIN company USING(company_id)
WHERE salary > (SELECT AVG(salary) FROM vacancy WHERE salary != 0);

--Getting list of all vacancies with keyword
SELECT company_name, vacancies, salary, url_vacancy
FROM vacancy
JOIN company USING(company_id)
WHERE vacancies LIKE '%{word.capitalize()}%'