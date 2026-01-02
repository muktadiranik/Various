import sqlite3

connection = sqlite3.connect("test.db")
cursor = connection.cursor()


def print_database():
    try:
        result = cursor.execute(
            "SELECT id, FName, LName, Age, Address, Salary, HireDate FROM Employees"
        )
        print(result)
        for row in result:
            print(row)
    except sqlite3.OperationalError:
        print("The Table Doesn't Exist")
    except:
        print("Couldn't Retrieve Data From Database")


print_database()


def create_table():
    try:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS Employees (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, FastName TEXT NOT NULL, LastName TEXT NOT NULL, Age INT NOT NULL, Address TEXT, Salary REAL, HireDate TEXT);"
        )
        connection.commit()
        print("Table Created")
    except sqlite3.OperationalError:
        print("Table Already Exists")
    except:
        print("Table Creation Failed")


create_table()


def seed_database():
    try:
        connection.execute(
            "INSERT INTO Employees (FastName, LastName, Age, Address, Salary, HireDate) VALUES ('Derek', 'Banas', 41, '123 Main St', '500,000', date('now'))"
        )
        connection.commit()
        print("Employee Added")
    except sqlite3.OperationalError:
        print("Table Doesn't Exist")
    except:
        print("Employee Addition Failed")


seed_database()


def update_database():
    try:
        connection.execute("UPDATE Employees SET Address = '121 Main St' WHERE ID=2")
        connection.commit()
        print("Employee Updated")
    except sqlite3.OperationalError:
        print("Table Doesn't Exist")
    except:
        print("Employee Update Failed")


update_database()


def delete_database_data():
    try:
        items = cursor.execute("SELECT * FROM Employees")
        for row in items:
            connection.execute(f"DELETE FROM Employees WHERE ID={row[0]}")
            connection.commit()
        print("Employee Deleted")
    except sqlite3.OperationalError:
        print("Table Doesn't Exist")
    except:
        print("Employee Deletion Failed")


delete_database_data()


def drop_table():
    try:
        connection.execute("DROP TABLE Employees")
        connection.commit()
        print("Table Dropped")
    except sqlite3.OperationalError:
        print("Table Doesn't Exist")
    except:
        print("Table Deletion Failed")


drop_table()


def alter_table():
    try:
        create_table()
        seed_database()
        connection.execute("ALTER TABLE Employees ADD COLUMN 'Image' BLOB DEFAULT NULL")
        connection.commit()
        print("Table Altered")
    except sqlite3.OperationalError as e:
        print(f"Operational Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


alter_table()


cursor.execute("PRAGMA table_info(Employees)")
rows = cursor.fetchall()
row_names = [item[1] for item in rows]
print(rows)
print(row_names)

cursor.execute("SELECT COUNT(*) FROM Employees")
count = cursor.fetchall()
print(count)

print(cursor.execute("SELECT SQLITE_VERSION()").fetchall())


with connection:
    connection.row_factory = sqlite3.Row
    cursor.execute("SELECT * FROM Employees")
    rows = cursor.fetchall()
    for row in rows:
        print(row[0], row[1], row[2], row[3], row[4], row[5], row[6])


with open("dump.sql", "w") as file:
    for line in connection.iterdump():
        file.write("%s\n" % line)

connection.close()
