CREATE .env file:
```
BOT_TOKEN=your_api_telegram_bot
WEATHER_API_KEY=your_api_weather
```

launch:


```
docker build -t tg-calories-bot .

docker run --name tg-bot --env-file .env tg-calories-bot
```
