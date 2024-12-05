# 🌟 SEAROS

Система выполнения произвольных запросов по расписанию
***

## 📖 Описание

SEAROS — это инструмент для автоматизации выполнения запросов к базам данных или внешним сервисам по расписанию.

Основные возможности:

* Планирование запросов с использованием расписания
* Админка для ручного управления задачами
* Автоматический перезапуск задач в случае сбоя
* Наличие REAS API

***

## 🛠️ Стек

* Python — основной язык разработки
* FastAPI — создание веб-приложений и REST API
* SQLAlchemy — ORM и работа с базами данных
* Pydantic — валидация и управление данными
* Celery — обработка фоновых задач
* Redis — брокер сообщений для Celery
* Requests — выполнение HTTP-запросов
* SQLAdmin — веб-интерфейс для управления базами данных
* Starlette — ASGI-фреймворк для FastAPI
* python-dotenv — работа с переменными окружения

***

## ⚙️ Требования

* Python 3.12+
* Redis сервер
* Зависимости из файла `requirements.txt`

***

## 🚀 Установка и настройка

1. Клонирование репозитория

```shell
git clone https://github.com/horizon343/searos.git
```

2. Установка зависимостей

```shell
pip install -r requirements.txt
```

3. Настройка переменных окружения

Создайте файл .env и добавьте:

* `ADMIN_AUTH_SECRET_KEY=<СЕКРЕТНЫЙ_КЛЮЧ_АВТОРИЗАЦИИ>`
* `SMTP_PORT=<ПОРТ_SMTP>`
* `SMTP_SERVER=<СЕРВЕР>`
* `SMTP_SENDER_EMAIL=<EMAIL_АДРЕС_ОТПРАВИТЕЛЯ>`
* `SMTP_PASSWORD=<ПАРОЛЬ_SMTP_СЕРВЕРА>`

***

## ▶️ Запуск проекта

1. Запуск Redis сервера

```shell
redis-server
```

2. Запуск Celery worker

```shell
celery -A celery_folder.celery_tasks worker --loglevel=INFO
```

3. Запуск FastAPI

```shell
uvicorn main:app --reload
```

***

## 🛡️ Админка

Админка доступна по пути [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)
