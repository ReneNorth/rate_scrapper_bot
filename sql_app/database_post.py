import psycopg2

conn = psycopg2.connect(database="rates_db",
                        host="localhost",
                        user="rene",
                        password="evilpostgresqlbird",
                        port="5432")

cursor = conn.cursor()
# почему не сработало изначально?
# cursor.execute("CREATE TABLE rates (ID INT PRIMARY KEY NOT NULL, NAME TEXT NOT NULL);")
# conn.commit()
cursor.execute("SELECT * FROM rates;")
# cursor.execute("INSERT INTO rates (ID, NAME) VALUES (1, 'first');")

# conn.commit()
count = cursor.rowcount
print(cursor.fetchone())