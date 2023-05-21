

CREATE TABLE companies
(
	company_id int PRIMARY KEY,
	company_name varchar UNIQUE NOT null
);

CREATE TABLE vacancies
(
	vacancy_id serial PRIMARY KEY,
	vacancy_name text NOT null,
	salary INT,
	company_name text NOT null,
	vacancy_url varchar NOT null
);

ALTER TABLE vacancies ADD CONSTRAINT  fk_company_name FOREIGN KEY(company_name) REFERENCES companies(company_name)