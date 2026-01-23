import aiohttp
import logging

logger = logging.getLogger(__name__)

# Получение температуры
async def get_weather(city: str, api_key: str):
    WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather?q={}&appid={}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(WEATHER_URL.format(city, api_key)) as response:
                if response.status == 200:
                    data = await response.json()
                    return round(data['main']['temp'] - 273.15, 1)
        except Exception as e:
            logger.exception(f"Ошибка при получении погоды: {e}")
    return None


# Получение калорийности продукта
async def get_food_info(product_name: str):
    url = f"https://world.openfoodfacts.org/cgi/search.pl?action=process&search_terms={product_name}&json=true"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    products = data.get("products", [])
                    if products:
                        first_product = products[0]
                        return {
                            'name': first_product.get('product_name', 'Неизвестно'),
                            'calories': first_product.get('nutriments', {}).get('energy-kcal_100g', 0)
                        }
        except Exception as e:
            logger.exception(f"Ошибка при получении информации о еде: {e}")
    return None
