# handlers.py
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BufferedInputFile
from states import Profile
import aiohttp

from utils import plot_progress, calculate_calories
from services import get_food_info, get_weather
from config import WEATHER_API_KEY
# import logging

# logger = logging.getLogger(__name__)

router = Router()
users = {}

@router.message(Command("set_profile"))
async def start_profile(message: Message, state: FSMContext):
    user_id = message.from_user.id
    # logger.info('Получено сообщение: /set_profile')

    if user_id not in users:
        users[user_id] = {
            "logged_water": [0],
            "logged_calories": [0],
            "burned_calories": 0
        }
    await message.reply("Введите ваш вес (в кг):")
    await state.set_state(Profile.weight)

@router.message(Profile.weight)
async def process_weight(message: Message, state: FSMContext):
    await state.update_data(weight=float(message.text))
    users[message.from_user.id]["weight"] = float(message.text)
    await message.reply("Введите ваш рост (в см):")
    await state.set_state(Profile.height)

@router.message(Profile.height)
async def process_height(message: Message, state: FSMContext):
    await state.update_data(height=float(message.text))
    users[message.from_user.id]["height"] = float(message.text)

    await message.reply("Введите ваш возраст:")
    await state.set_state(Profile.age)

@router.message(Profile.age)
async def process_age(message: Message, state: FSMContext):
    await state.update_data(age=float(message.text))
    users[message.from_user.id]["age"] = float(message.text)

    await message.reply("Сколько минут активности у вас в день?")
    await state.set_state(Profile.activity)

@router.message(Profile.activity)
async def process_activity(message: Message, state: FSMContext):
    await state.update_data(activity=float(message.text))
    users[message.from_user.id]["activity"] = float(message.text)

    await message.reply("В каком городе вы находитесь?")
    await state.set_state(Profile.city)

@router.message(Profile.city)
async def process_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)

    users[message.from_user.id]["city"] = message.text

    temp = await get_weather(message.text, WEATHER_API_KEY)
    if temp == None:
      await message.answer('Ошибка: название города некорректно! Повторите ввод.')
      await state.set_state(Profile.city)
    else:
      await state.update_data(city_temp = temp)

    #   users[message.from_user.id]["city_temp"] = temp
      user_data = users.get(message.from_user.id, {})
      user_data['city_temp'] = temp
      users[message.from_user.id] = user_data

      await calculate_calories(state, message, users)
      await state.clear()

@router.message(Command("log_water"))
async def logging_water(message: Message, state: FSMContext):
    args = message.text.split(maxsplit=1)
    # logger.info('Получено сообщение: /log_water')
    if len(args) < 2:
        await message.answer(
            "Ошибка: не передан объем выпитой воды. Пример:\n"
            "/log_water <volume>"
        )
        return

    try:
        water_volume = float(args[1])
        data = await state.get_data()
        new_logged_water = (data.get('logged_water', [0]))
        new_logged_water.append(water_volume)
        await state.update_data(logged_water = new_logged_water)

        user_data = users.get(message.from_user.id, {})
        user_data['logged_water'] = new_logged_water
        users[message.from_user.id] = user_data
    except ValueError:
        await message.answer(
            "Ошибка: неправильный формат команды. Пример:\n"
            "/log_water <volume>"
        )
        return
    await message.answer(
        f"Вода добавлена!\n Осталось выпить за сегодня {data.get('water_goal', 1500) - sum(new_logged_water)} мл"
        )

@router.message(Command("log_food"))
async def logging_food(message: Message, state: FSMContext):
    args = message.text.split(maxsplit=1)
    # logger.info('Получено сообщение: /log_food')

    if len(args) < 2:
        await message.answer(
            "Ошибка: не передана информация о приеме пищи!"
        )
        return

    try:
        food_name = args[1]
        new_food = await get_food_info(food_name)
        new_calories = new_food['calories']

        await message.reply(f'{new_food["name"]} - {new_calories} ккал на 100 г. Сколько грамм вы съели?')
        await state.update_data(food_calories=new_calories)
        await state.set_state(Profile.food_weight)

    except ValueError:
        await message.answer(
            "Ошибка: неправильный формат команды. Пример:\n"
            "/log_food <food_name>"
        )
        return

@router.message(Profile.food_weight)
async def log_weight_food(message: Message, state: FSMContext):
  weight_food = float(message.text)
  await state.update_data(food_weight = weight_food)

  data = await state.get_data()
  new_calories = data.get('food_calories', 0) * weight_food / 100
  # eaten_calories = users[message.from_user.id]['logged_calories']
  eaten_calories = users.get(message.from_user.id, {}).get('logged_calories', [0])
  eaten_calories.append(new_calories)

  await state.update_data(logged_calories = eaten_calories)
  user_data = users.get(message.from_user.id, {})
  user_data['logged_calories'] = eaten_calories
  users[message.from_user.id] = user_data

  await message.answer(
      f"Еда добавлена!\n Всего за день съедено {sum(eaten_calories)} из {users.get(message.from_user.id, {}).get('calorie_goal', 2500)} ккал"
  )
  await state.clear()

@router.message(Command('log_workout'))
async def logging_workout(message: Message, state: FSMContext):
    # logger.info('Получено сообщение: /log_workout')
    args = message.text.split(maxsplit=2)

    if len(args) < 3:
        await message.answer(
            "Ошибка: не передана информация о тренировке! Пример:\n"
            "/log_workout <workout_type> <workout_calories>"
        )
        return

    try:
        workout_type = args[1]
        workout_time = float(args[2])
        extra_water = workout_time // 30 * 200
        # 200 kkal per every 50 min of cardio
        workout_calories = round(workout_time / 50 * 200, 1)

        await state.update_data(burned_calories = workout_calories)
        await state.update_data(logged_workout = workout_type)
        
        user_data = users.get(message.from_user.id, {})
        user_data['burned_calories'] = user_data.get('burned_calories', 0) + workout_calories
        users[message.from_user.id] = user_data


    except ValueError:
        await message.answer(
            "Ошибка: неправильный формат команды. Пример:\n"
            "/log_workout <workout_type> <workout_calories>"
        )
        return
    await message.answer(
        f"🏃‍♂️ {workout_type} {workout_time} минут - {workout_calories} ккал. Дополнительно: выпейте {extra_water} мл воды."
    )

@router.message(Command("check_progress"))
async def checking_progress(message: Message, state: FSMContext):

    # data = await state.get_data()
    data = users.get(message.from_user.id, {})
    # logger.info('Получено сообщение: /check_progress')

    await message.answer(
        f"""📊 Прогресс:
        Вода:
        - Выпито: {sum(data.get('logged_water', [0]))} мл из {data.get('water_goal', 1500)} мл.
        - Осталось: {data.get('water_goal', 1500) - sum(data.get('logged_water', [0])) if data.get('water_goal', 1500) > sum(data.get('logged_water', [0])) else 0} мл.

        Калории:
        - Потреблено: {sum(data.get('logged_calories', [0]))} ккал из {data.get('calorie_goal', 2500)} ккал.
        - Сожжено: {(data.get('burned_calories', 0))} ккал.
        - Баланс: {sum(data.get('logged_calories', [0])) - (data.get('burned_calories', 0))} ккал."""
    )

@router.message(Command("check_progress_graph"))
async def send_progress_graph(message: Message, state: FSMContext):
    # logger.info('Получено сообщение: /check_progress_graph')
    data = users.get(message.from_user.id, {})
    water_data = data.get('logged_water', [0])
    water_goal = data.get('water_goal', 1500)
    calorie_data = data.get('logged_calories', [0])
    food_goal = data.get('calorie_goal', 2500)

    graph_image = await plot_progress(water_data, water_goal, calorie_data, food_goal)
    graph_image.seek(0)
    graph_image_file = BufferedInputFile(graph_image.read(), filename="progress_graph.png")

    await message.answer("Вот ваш прогресс по воде и калориям:")
    await message.answer_photo(graph_image_file)

# Функция для подключения обработчиков
def setup_handlers(dp):
    dp.include_router(router)