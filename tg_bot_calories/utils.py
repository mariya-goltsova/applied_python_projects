import matplotlib.pyplot as plt
from io import BytesIO
from aiogram.fsm.context import FSMContext

async def calculate_calories(state: FSMContext, message, users):

  data = await state.get_data()

  # if activity time per day > 50 min
  if data['activity'] > 50:
    act = 400
  else:
    act = 200 * data['activity'] / 25

  calories_goal = 10 * data['weight'] + 6.25 * data['height'] - 5 * data['age'] + act

  temp = 1000 if data['city_temp'] > 25 else 0
  water_goal = 30 * data['weight'] + 500 * (data['activity'] // 30) + 500 - temp

  await message.answer(f'''Ваша цель калорий: {calories_goal} ккал
  Цель воды: {water_goal} мл''')

  await state.update_data(water_goal=water_goal, calorie_goal=calories_goal)
  users[message.from_user.id]["water_goal"] = water_goal
  users[message.from_user.id]["calorie_goal"] = calories_goal
  return users

async def plot_progress(water_data, water_goal, calorie_data, food_goal, time_period='Сегодня'):
    fig, ax = plt.subplots()
    max_len = max(len(water_data), len(calorie_data))
    time_labels = range(max_len)
    water_data = water_data + [max(water_data)] * (max_len - len(water_data))
    calorie_data = calorie_data + [max(calorie_data)] * (max_len - len(calorie_data))

    ax.plot(time_labels, water_data, label="Вода (мл)", marker='o', color='b')
    plt.axhline(y=water_goal, color='y', linestyle='--', label = 'Цель воды')
    ax.plot(time_labels, calorie_data, label="Калории (ккал)", marker='o', color='r')
    plt.axhline(y=food_goal, color='g', linestyle='-.', label = 'Цель ккал')


    ax.set_xlabel("Время")
    ax.set_ylabel("Объем (мл) / Калории (ккал)")
    ax.set_title(f"Прогресс по воде и калориям за {time_period}")
    ax.legend()

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)

    return buf

