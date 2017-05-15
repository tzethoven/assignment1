import pymysql
from PyQt5.QtCore import QThread, pyqtSignal

# SQL thread class inherits from Qthread
class SQL_thread(QThread):

    # Create pyqtSignals to communicate with the GUI
    status = pyqtSignal(int)
    error = pyqtSignal(str)


    def __init__(self, objs, cred, name="powersystem"):
        # SQL_thread constructor
        QThread.__init__(self)
        self.objs = objs
        self.port, self.user, self.pw = cred
        self.cur = 0
        self.db_name = name
        self.sql_types = {str: "VARCHAR(650)", int: "INT", float: "REAL", bool: "BOOLEAN"}
        self.sql_bool = {True: 1, False: 0}
        self.foreign_keys = set()

    def __del__(self):
        self.wait()


    def run(self):
        # Overrides QThread method to run generate_db() function
        try:
            self.generate_db()
        except Exception as e:
            self.error.emit(e)



    def generate_db(self):
        self.cur = self.create_cur()

        # Check whether database exists already and if so, drop it
        self.cur.execute("SHOW DATABASES")
        if (self.db_name.lower(),) in {row for row in self.cur}:
            self.cur.execute("DROP DATABASE " + self.db_name)

        # Create new database and use it
        self.cur.execute("CREATE DATABASE " + self.db_name)
        self.cur.execute("USE " + self.db_name)

        # Loop through dictionary and fill the database
        self.process_objs()

        # Loop through fk columns and add foreign keys to them
        self.add_foreign_keys()

        # Close database connection
        self.cur.close()
        self.conn.close()

    def process_objs(self):
        # Loop through objs and process them
        n = len(self.objs)
        i = 1
        for obj in self.objs.items():
            self.process_obj(obj)
            # emit status signal to gui
            self.status.emit(100 * i / n)
            i += 1

    def process_obj(self, obj):
        # Select necessary properties of object and add it to the database
        obj_id, obj = obj
        obj_name = obj.__name__
        attrs = [(attr, getattr(obj, attr)) for attr in dir(obj) if attr[:2] + attr[-2:] != '____']
        self.add_to_db(obj_id, obj_name, attrs)

    def add_to_db(self, obj_id, obj_name, attrs):
        # Check whether the table doesn't exists yet, if not, create a new table
        if not self.table_exists(obj_name):
            self.create_table(obj_name, attrs)

        # Insert item into existing table
        self.insert_item(obj_id, obj_name, attrs)

    def create_table(self, name, attrs):
        # Loop through attributes to define table columns and build the sql query to create a new table
        # 767 is the max length of a VARCHAR primary key
        attr_str = name + "_id VARCHAR(767) PRIMARY KEY, "
        for (attr, val) in attrs:

            # If column is an id and doesn't point to different tables, flag the column to add a foreign key
            if type(val) == str and val[0] == "_" and not any(x in attr.lower() for x in
                                                              {"container", "equipment", "generatingunit"}):
                ref_table = self.objs[val].__name__
                self.foreign_keys.add((name, attr, ref_table,))

            attr_str += attr + " " + self.sql_types[type(val)]
            attr_str += ", "
        sql_str = "CREATE TABLE " + name + " (" + attr_str[:-2] + ")"

        self.cur.execute(sql_str)

    def insert_item(self, id, name, attrs):
        # Build sql query to insert item in existing table
        attr_str = name + "_id, "
        val_str = "\"" + id + "\", "

        #
        for (attr, val) in attrs:
            if type(val) == bool:
                val = self.sql_bool[val]
            attr_str += attr + ", "
            val_str += "\"" + str(val) + "\", "

            # If the column doesn't exist, add it to the table
            self.cur.execute("SHOW COLUMNS FROM " + name + " LIKE \'" + attr + "\'")
            if not [row for row in self.cur]:
                self.cur.execute("ALTER TABLE " + name + " ADD " + attr + " " + self.sql_types[type(val)])
        sql_str = "INSERT INTO " + name + " (" + attr_str[:-2] + ") VALUES (" + val_str[:-2] + ")"


        self.cur.execute(sql_str)

    def add_foreign_keys(self):
        # Loop through the flagged foreign key columns set and add foreign key to the columns
        for name, attr, ref_table in self.foreign_keys:
            sql_str = "ALTER TABLE " + name + " ADD FOREIGN KEY (" + attr + ") REFERENCES " + ref_table + "(" + \
                      ref_table + "_id)"
            # print(sql_str)
            self.cur.execute(sql_str)



    def table_exists(self, table):
        # Check whether table exists already
        self.cur.execute("SHOW TABLES")
        if (table.lower(),) in {row for row in self.cur}:
            return True
        else:
            return False

    def create_cur(self):
        # Connect to mySQL Server and create a cursor
        self.conn = pymysql.connect(host="localhost", port=self.port, user=self.user, passwd=self.pw, db="mysql", charset="utf8")
        return self.conn.cursor()


