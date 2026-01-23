launch:


```
docker build -t tg-calories-bot .

docker run --name tg-bot --env-file .env tg-calories-bot
```