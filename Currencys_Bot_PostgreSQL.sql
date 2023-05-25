drop table currencies;
CREATE TABLE currencies
	(
		id SERIAL PRIMARY KEY UNIQUE,
		currency_name VARCHAR,
		rate NUMERIC
	);

drop table admins;
CREATE TABLE admins
	(
		id INTEGER PRIMARY KEY UNIQUE,
		chat_id VARCHAR
	);
	
INSERT INTO admins(id, chat_id) VALUES (1,'388930488');
select*from admins
select*from currencies