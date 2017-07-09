import MySQLdb
import sqlite3

class Database:

    def __init__(self, testing=False):
        if testing: # Note: this isn't working
            self.connection = sqlite3.connect('polo.db')
        else:
            self.connection = MySQLdb.connect(host="35.185.193.153", user="root", passwd="", db="guestbook") 

    def write(self, query, parameters=None):
        self.cursor = self.connection.cursor(MySQLdb.cursors.SSDictCursor)
        try:
            self.cursor.execute(query, parameters)
            self.connection.commit()
        except:
            self.connection.rollback()
            raise

    def write_dict(self, table, d):
        placeholders = ', '.join(['%s'] * len(d))
        columns = ', '.join(d.keys())
        sql = "INSERT INTO %s ( %s ) VALUES ( %s )" % (table, columns, placeholders)
        self.write(sql, d.values())

    def get_reader(self, query):
        cursor = self.connection.cursor(MySQLdb.cursors.SSDictCursor)
        cursor.execute(query)
        return cursor

    def listen(self, query):
        cursor = self.connection.cursor(MySQLdb.cursors.SSDictCursor)
        cursor.execute(query)
        while True:
            rows = cursor.fetchmany(size=1000)
            for r in rows:
                print(r)
            if not rows: break

    def __del__(self):
        self.connection.close()


if __name__ == "__main__":

    db = Database()

    create_query = "CREATE TABLE basic_python_database (name VARCHAR(255), age INTEGER)"
    db.write(create_query)

    db.write_dict('basic_python_database', {'age': '24', 'name': 'Miles'})

    query = """
        INSERT INTO basic_python_database
        (`name`, `age`)
        VALUES
        ('Mike', 21),
        ('Michael', 21),
        ('Imran', 21)
        """

    db.write(query)

    select_query = """
        SELECT * FROM basic_python_database
        WHERE age = 21
        """

    people = db.get_reader(select_query)
    for person in people:
        print("Found %s " % person['name'])

    del_query = "DELETE FROM basic_python_database"
    db.write(del_query)

