import mysql.connector
import yaml

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

db_conn = mysql.connector.connect(host=app_config['datastore']['hostname'], user=app_config['datastore']['user'], password=app_config['datastore']['password'], database=app_config['datastore']['db'])

db_cursor = db_conn.cursor()

db_cursor.execute('''
           CREATE TABLE book_withdrawal
          (id INT NOT NULL AUTO_INCREMENT,
           withdrawal_id VARCHAR(36) NOT NULL,
           book_name VARCHAR(250) NOT NULL,
           genre VARCHAR(100) NOT NULL,
           num_of_pages INTEGER NOT NULL,
           days_allowed INTEGER NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           trace_id VARCHAR(100) NOT NULL,
           CONSTRAINT book_withdrawal_pk PRIMARY KEY (id))
           ''')

db_cursor.execute('''
         CREATE TABLE book_return
         (id INT NOT NULL AUTO_INCREMENT,
          return_id VARCHAR(36) NOT NULL,
          book_name VARCHAR(250) NOT NULL,
          days_overdue INTEGER NOT NULL,
          expected_fine REAL NOT NULL,
          timestamp VARCHAR(100) NOT NULL,
          date_created VARCHAR(100) NOT NULL,
          trace_id VARCHAR(100) NOT NULL,
          CONSTRAINT book_return_pk PRIMARY KEY (id))
''')

db_conn.commit()
db_conn.close()