import sqlite3

connection = sqlite3.connect('yt_database.db')
cursor = connection.cursor()

# Создаем таблицу Users
cursor.execute('''
CREATE TABLE IF NOT EXISTS Users (
id INTEGER PRIMARY KEY AUTOINCREMENT,
chat_id INTEGER,
username TEXT,
name TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Records (
id INTEGER PRIMARY KEY AUTOINCREMENT,
chat_id INTEGER,
time TEXT
)
''')

#cursor.execute(f"INSERT INTO Users (chat_id, username, name) VALUES (4847294, @admin, Dima);")


def add_user(chat_id: int, username: str, name:str):
    connection = sqlite3.connect('yt_database.db')
    cursor = connection.cursor()
    cursor.execute(f"INSERT INTO Users (chat_id, username, name) VALUES ({chat_id}, '{username}', '{name}');")
    connection.commit()
    connection.close()


def add_record(chat_id: int):
    connection = sqlite3.connect('yt_database.db')
    cursor = connection.cursor()
    cursor.execute(f"INSERT INTO Records (chat_id, time) VALUES ({chat_id}, datetime('now'));")
    connection.commit()
    connection.close()


# Сохраняем изменения и закрываем соединение
connection.commit()
connection.close()