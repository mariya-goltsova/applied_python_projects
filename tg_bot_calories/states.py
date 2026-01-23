from aiogram.fsm.state import State, StatesGroup

# FSM
class Profile(StatesGroup):
    weight = State()
    height = State()
    age = State()
    activity = State() # activity per day
    city = State()
    city_temp = State()
    water_goal = State()
    calorie_goal = State()
    logged_water = State()
    logged_calories = State()
    logged_workout = State()
    burned_calories = State()
    food_weight = State()
    food_calories = State()
