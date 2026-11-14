from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import bcrypt
import sqlite3

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модели для приема данных от пользователя
class UserAuth(BaseModel):
    email: str
    password: str

def get_db_connection():
    conn = sqlite3.connect('tickets.db')
    conn.row_factory = sqlite3.Row 
    return conn

# ОБРАБОТЧИК 1: Получить список всех рейсов
@app.get("/api/routes")
def get_routes():
    conn = get_db_connection()
    routes = conn.execute('SELECT * FROM routes').fetchall()
    conn.close()
    return [dict(route) for route in routes]

# ОБРАБОТЧИК 2: Регистрация
@app.post("/api/register")
def register(user: UserAuth):
    conn = get_db_connection()
    
    existing_user = conn.execute('SELECT * FROM users WHERE email = ?', (user.email,)).fetchone()
    if existing_user:
        conn.close()
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")
    
    # Хешируем пароль через bcrypt напрямую
    password_bytes = user.password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    # Безопасный SQL-запрос
    conn.execute('INSERT INTO users (email, password_hash) VALUES (?, ?)', (user.email, hashed_password))
    conn.commit()
    conn.close()
    
    return {"message": "Пользователь успешно зарегистрирован"}

# ОБРАБОТЧИК 3: Вход (Авторизация)
@app.post("/api/login")
def login(user: UserAuth):
    conn = get_db_connection()
    
    db_user = conn.execute('SELECT * FROM users WHERE email = ?', (user.email,)).fetchone()
    conn.close()
    
    if not db_user:
        raise HTTPException(status_code=400, detail="Неверный email или пароль")
    
    # Проверяем пароль через bcrypt
    password_bytes = user.password.encode('utf-8')
    hashed_bytes = db_user['password_hash'].encode('utf-8')
    
    if not bcrypt.checkpw(password_bytes, hashed_bytes):
        raise HTTPException(status_code=400, detail="Неверный email или пароль")
    
    return {"message": "Вход выполнен успешно", "user_id": db_user['id']}

# ОБРАБОТЧИК 4: Получить один рейс по ID
@app.get("/api/routes/{route_id}")
def get_one_route(route_id: int):
    conn = get_db_connection()
    route = conn.execute('SELECT * FROM routes WHERE id = ?', (route_id,)).fetchone()
    conn.close()
    
    if not route:
        raise HTTPException(status_code=404, detail="Рейс не найден")
        
    return dict(route)

# ОБРАБОТЧИК 5 (Бонус для варианта с заказами): Создание заказа
class OrderCreate(BaseModel):
    user_id: int
    route_id: int
    seat_number: int

@app.post("/api/orders")
def create_order(order: OrderCreate):
    conn = get_db_connection()
    
    # Сохраняем заказ в базу
    conn.execute(
        'INSERT INTO orders (user_id, route_id, seat_number) VALUES (?, ?, ?)', 
        (order.user_id, order.route_id, order.seat_number)
    )
    conn.commit()
    conn.close()
    
    return {"message": "Заказ успешно создан"}

# ОБРАБОТЧИК 6: Получить заказы пользователя (для профиля)
@app.get("/api/orders/user/{user_id}")
def get_user_orders(user_id: int):
    conn = get_db_connection()
    # Сложный SQL-запрос: соединяем таблицу заказов и рейсов, чтобы узнать города и цену
    orders = conn.execute('''
        SELECT orders.id, orders.seat_number, routes.from_city, routes.to_city, routes.train_number, routes.price 
        FROM orders 
        JOIN routes ON orders.route_id = routes.id 
        WHERE orders.user_id = ?
    ''', (user_id,)).fetchall()
    conn.close()
    return [dict(order) for order in orders]

# ОБРАБОТЧИК 7: Удаление аккаунта
class UserDelete(BaseModel):
    password: str

@app.delete("/api/users/{user_id}")
def delete_user(user_id: int, user_data: UserDelete):
    conn = get_db_connection()
    
    # 1. Ищем пользователя
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # 2. Проверяем, правильно ли введен пароль
    password_bytes = user_data.password.encode('utf-8')[:72]
    hashed_bytes = user['password_hash'].encode('utf-8')
    
    if not bcrypt.checkpw(password_bytes, hashed_bytes):
        conn.close()
        raise HTTPException(status_code=400, detail="Неверный пароль. Удаление отменено.")
    
    # 3. Удаляем сначала все заказы пользователя (чтобы не было ошибки базы данных)
    conn.execute('DELETE FROM orders WHERE user_id = ?', (user_id,))
    
    # 4. Удаляем самого пользователя
    conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
    
    conn.commit()
    conn.close()
    
    return {"message": "Аккаунт успешно удален"}