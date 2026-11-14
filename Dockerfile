# Берем официальный образ Linux с Python
FROM python:3.11-slim

# Создаем рабочую папку внутри контейнера
WORKDIR /app

# Копируем список библиотек и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все остальные файлы проекта
COPY . .

# Запускаем создание базы данных и затем сам сервер
CMD ["sh", "-c", "python database.py && uvicorn main:app --host 0.0.0.0 --port 8000"]