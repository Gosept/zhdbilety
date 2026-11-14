import sqlite3

# Подключаемся к базе данных (если файла нет, он создастся автоматически)
conn = sqlite3.connect('tickets.db')
cursor = conn.cursor()

# 1. СОЗДАНИЕ ТАБЛИЦ

# Таблица пользователей
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
)
''')

# Таблица рейсов
cursor.execute('''
CREATE TABLE IF NOT EXISTS routes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_city TEXT NOT NULL,
    to_city TEXT NOT NULL,
    train_number TEXT NOT NULL,
    price INTEGER NOT NULL,
    dep_time TEXT NOT NULL,
    arr_time TEXT NOT NULL,
    duration TEXT NOT NULL
)
''')

# Таблица заказов (связывает пользователя и рейс)
cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    route_id INTEGER,
    seat_number INTEGER,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (route_id) REFERENCES routes (id)
)
''')

# 2. ЗАПОЛНЕНИЕ ТАБЛИЦЫ РЕЙСОВ (15 записей)

# Проверяем, есть ли уже данные в таблице, чтобы не дублировать их при каждом запуске
cursor.execute('SELECT COUNT(*) FROM routes')
if cursor.fetchone()[0] == 0:
    print("Заполняем базу данными...")
    
    routes_data = [
        ("Москва", "Санкт-Петербург", "001А", 2500, "10:00", "14:00", "4 часа"),
        ("Москва", "Санкт-Петербург", "002Б", 3000, "14:00", "18:00", "4 часа"),
        ("Москва", "Казань", "003В", 3200, "08:00", "20:00", "12 часов"),
        ("Москва", "Нижний Новгород", "004Г", 1800, "12:00", "16:00", "4 часа"),
        ("Санкт-Петербург", "Москва", "005Д", 2600, "09:00", "13:00", "4 часа"),
        ("Москва", "Сочи", "006Е", 4500, "15:00", "15:00", "24 часа"),
        ("Москва", "Екатеринбург", "007Ж", 3800, "11:00", "23:00", "12 часов"),
        ("Казань", "Москва", "008З", 3300, "16:00", "04:00", "12 часов"),
        ("Нижний Новгород", "Москва", "009И", 1900, "18:00", "22:00", "4 часа"),
        ("Москва", "Санкт-Петербург", "010К", 2200, "20:00", "00:00", "4 часа"),
        ("Санкт-Петербург", "Казань", "011Л", 4000, "07:00", "19:00", "12 часов"),
        ("Москва", "Нижний Новгород", "012М", 1700, "22:00", "02:00", "4 часа"),
        ("Москва", "Сочи", "013Н", 4800, "10:00", "10:00", "24 часа"),
        ("Москва", "Казань", "014П", 3500, "19:00", "07:00", "12 часов"),
        ("Санкт-Петербург", "Сочи", "015Р", 5500, "12:00", "12:00", "36 часов")
    ]
    
    # Вставляем данные в таблицу
    cursor.executemany('''
    INSERT INTO routes (from_city, to_city, train_number, price, dep_time, arr_time, duration)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', routes_data)
    
    print("База данных успешно заполнена 15 рейсами!")

# Сохраняем изменения и закрываем соединение
conn.commit()
conn.close()