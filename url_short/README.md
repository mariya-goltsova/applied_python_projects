# Описание API
POST /links/shorten

GET /{short_code}

DELETE /links/{short_code}

PUT /links/{short_code}

GET /links/{short_code}/stats

# Пример запроса
POST /links/shorten

{

 "original_url": "https://google.com"

}


## Для проверки ф-ии expired links:

POST:

{
 "original_url": "https://google.com",
 "expires_at": "2026-03-11T16:41:00"
}


# Запуск

docker-compose up --build