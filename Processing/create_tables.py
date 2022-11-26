import sqlite3

conn = sqlite3.connect('stats.sqlite')

c = conn.cursor()
c.execute('''
        CREATE TABLE stats
        (id INTEGER PRIMARY KEY ASC,
        num_bk_withdrawals INTEGER NOT NULL,
        num_bk_returns INTEGER NOT NULL,
        max_overdue_length INTEGER NOT  NULL,
        max_overdue_fine INTEGER NOT NULL,
        longest_book_withdrawn INTEGER NOT NULL,
        last_updated VARCHAR(100) NOT NULL)

''')

conn.commit()
conn.close()