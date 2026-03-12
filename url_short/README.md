# URL Shortener API

API-сервис для сокращения ссылок, получения статистики и управления ими.

Сервис позволяет создавать короткие ссылки для длинных URL, получать аналитику переходов, управлять ссылками и группировать их по проектам.

Пример аналогичных сервисов:
- tinyURL
- bitly

---

# Функциональность

## Основные функции

### Создание короткой ссылки

Создает короткую ссылку для длинного URL.

**POST /links/shorten**

Параметры:

- original_url — оригинальная ссылка
- custom_alias — пользовательский alias (необязательно)
- expires_at — дата истечения ссылки
- project — название проекта

Пример запроса:

POST /links/shorten


Body:


{
"original_url": "https://google.com
",
"project": "work"
}


Ответ:


{
"short_url": "http://localhost:8000/abc123
"
}


---

### Переход по короткой ссылке

Перенаправляет на оригинальный URL.


GET /{short_code}


Пример:


GET /abc123


---

### Обновление ссылки

Позволяет изменить оригинальный URL.


PUT /links/{short_code}


Пример запроса:


PUT /links/abc123


Body:


{
"original_url": "https://youtube.com
"
}


---

### Удаление ссылки

Удаляет связь между короткой и оригинальной ссылкой.


DELETE /links/{short_code}


Пример:


DELETE /links/abc123


---

### Получение статистики

Возвращает статистику переходов по ссылке.


GET /links/{short_code}/stats


Ответ:


{
"original_url": "https://google.com
",
"created_at": "2024-05-01T10:00:00",
"click_count": 5,
"last_used_at": "2024-05-01T11:00:00"
}


---

# Дополнительные функции

### Поиск ссылки по оригинальному URL


GET /links/search?original_url=https://google.com


Ответ:


{
"short_code": "abc123",
"original_url": "https://google.com
"
}


---

### Получить все ссылки


GET /links


---

### Группировка ссылок по проекту


GET /links/project/{project_name}


Пример:


GET /links/project/work


---

### Получить истекшие ссылки


GET /links/expired


---

### Удаление неиспользуемых ссылок

Удаляет ссылки, которые не использовались N дней.


DELETE /links/cleanup?days=30


---

# Кэширование

В сервисе используется **Redis** для кэширования популярных ссылок.

При обращении к короткой ссылке:

1. Проверяется Redis
2. Если ссылка есть в кэше — выполняется редирект
3. Если нет — ссылка берется из PostgreSQL

При обновлении или удалении ссылки кэш очищается.

---

# База данных

Используется **PostgreSQL**.

## Таблица links

| Поле | Тип | Описание |
|-----|-----|-----|
| id | integer | идентификатор |
| short_code | string | короткий код |
| original_url | string | оригинальный URL |
| created_at | datetime | дата создания |
| expires_at | datetime | дата истечения |
| click_count | integer | количество переходов |
| last_used_at | datetime | последний переход |
| project | string | проект |

---

# Технологии

- FastAPI
- PostgreSQL
- Redis
- SQLAlchemy
- Docker
- Docker Compose

---

# Запуск проекта

## 1 Клонировать репозиторий


git clone https://github.com/your-username/url-shortener

cd url-shortener


---

## 2 Запустить Docker


docker compose up --build


---

## 3 Открыть API

Swagger документация:


http://localhost:8000/docs


---

# Тестирование API

В Swagger можно:

- создавать ссылки
- обновлять
- удалять
- получать статистику
- тестировать дополнительные функции

---

# Пример работы

1. Создаем ссылку


POST /links/shorten

{
"original_url": "https://google.com
"
}


Ответ:


http://localhost:8000/abc123


---

2. Открываем ссылку


GET /abc123


Происходит редирект на Google.

---

3. Получаем статистику


GET /links/abc123/stats


---

# Автор
Гольцова Мария Михайловна — URL Shortener API
