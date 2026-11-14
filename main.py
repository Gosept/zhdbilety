from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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

# Раздаем папку с картинками
app.mount("/images", StaticFiles(directory="images"), name="images")

class UserAuth(BaseModel):
    email: str
    password: str

def get_db_connection():
    conn = sqlite3.connect('tickets.db')
    conn.row_factory = sqlite3.Row 
    return conn

# API ОБРАБОТЧИКИ
@app.get("/api/routes")
def get_routes():
    conn = get_db_connection()
    routes = conn.execute('SELECT * FROM routes').fetchall()
    conn.close()
    return [dict(route) for route in routes]

@app.post("/api/register")
def register(user: UserAuth):
    conn = get_db_connection()
    existing_user = conn.execute('SELECT * FROM users WHERE email = ?', (user.email,)).fetchone()
    if existing_user:
        conn.close()
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")
    
    password_bytes = user.password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    conn.execute('INSERT INTO users (email, password_hash) VALUES (?, ?)', (user.email, hashed_password))
    conn.commit()
    conn.close()
    return {"message": "Пользователь успешно зарегистрирован"}

@app.post("/api/login")
def login(user: UserAuth):
    conn = get_db_connection()
    db_user = conn.execute('SELECT * FROM users WHERE email = ?', (user.email,)).fetchone()
    conn.close()
    
    if not db_user:
        raise HTTPException(status_code=400, detail="Неверный email или пароль")
    
    password_bytes = user.password.encode('utf-8')[:72]
    hashed_bytes = db_user['password_hash'].encode('utf-8')
    
    if not bcrypt.checkpw(password_bytes, hashed_bytes):
        raise HTTPException(status_code=400, detail="Неверный email или пароль")
    
    return {"message": "Вход выполнен успешно", "user_id": db_user['id']}

@app.get("/api/routes/{route_id}")
def get_one_route(route_id: int):
    conn = get_db_connection()
    route = conn.execute('SELECT * FROM routes WHERE id = ?', (route_id,)).fetchone()
    conn.close()
    if not route:
        raise HTTPException(status_code=404, detail="Рейс не найден")
    return dict(route)

class OrderCreate(BaseModel):
    user_id: int
    route_id: int
    seat_number: int

@app.post("/api/orders")
def create_order(order: OrderCreate):
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO orders (user_id, route_id, seat_number) VALUES (?, ?, ?)', 
        (order.user_id, order.route_id, order.seat_number)
    )
    conn.commit()
    conn.close()
    return {"message": "Заказ успешно создан"}

@app.get("/api/orders/user/{user_id}")
def get_user_orders(user_id: int):
    conn = get_db_connection()
    orders = conn.execute('''
        SELECT orders.id, orders.seat_number, routes.from_city, routes.to_city, routes.train_number, routes.price 
        FROM orders 
        JOIN routes ON orders.route_id = routes.id 
        WHERE orders.user_id = ?
    ''', (user_id,)).fetchall()
    conn.close()
    return [dict(order) for order in orders]

# РАЗДАЧА СТРАНИЦ (HTML, CSS, JS)
@app.get("/")
def read_root():
    return FileResponse("index.html")

# Я добавил маршрут для index.html!
@app.get("/index.html")
def read_index():
    return FileResponse("index.html")

@app.get("/catalog.html")
def read_catalog():
    return FileResponse("catalog.html")

@app.get("/item.html")
def read_item():
    return FileResponse("item.html")

@app.get("/order.html")
def read_order():
    return FileResponse("order.html")

@app.get("/profile.html")
def read_profile():
    return FileResponse("profile.html")

@app.get("/contacts.html")
def read_contacts():
    return FileResponse("contacts.html")

@app.get("/script.js")
def read_js():
    return FileResponse("script.js")

@app.get("/style.css")
def read_css():
    return FileResponse("style.css")
    
    @app.get("/api/users")
def get_all_users():
    conn = get_db_connection()
    users = conn.execute('SELECT id, email, password_hash FROM users').fetchall()
    conn.close()
    return [dict(user) for user in users]