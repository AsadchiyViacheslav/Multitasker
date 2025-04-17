# Backend for My Study Multitasker App 🎯


## 📦 Стек технологий:
- Python 3.10+
- FastAPI
- SQLAlchemy
- PostgreSQL (локально)
- Redis (через Docker)
- JWT авторизация
- Pydantic
- Swagger

## ⚙️ Установка (Локально себе)

1. Клонировать проект:

```bash
git clone https://github.com/AsadchiyViacheslav/Multitasker.git
```

2. Создать виртуальное окружение:

```
python -m venv venv
venv\Scripts\activate
```

3. Установить нужные библиотеки 

4. Создать .env файл на основе .env.example:

```
SECRET_KEY=...
ALGORITHM=HS256
DB_HOST=localhost
DB_PORT=5432
DB_USER=...
DB_PASSWORD=...
DB_NAME=...
REDIS_HOST=localhost
REDIS_PORT=6379
```

5. Подключить Redis через Docker:

```
docker run -d -p 6379:6379 --name redis redis
```

6. Запуск для тестирования:

```
uvicorn app.main:app --reload
```
