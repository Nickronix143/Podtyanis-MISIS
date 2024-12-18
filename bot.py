import telebot
import os
from dotenv import load_dotenv
from telebot import types
from text import *

load_dotenv()

bot = telebot.TeleBot(os.getenv('TELEGRAM_API_TOKEN'))
ADMIN_CHANNEL_ID = os.getenv('ADMIN_CHANNEL_ID')
user_data = {}

def get_nutrition_plan(weight, goal, gender):
    # Словарь с планами питания по категориям веса
    plans_set_male = {
        (50, 55): set_male_50_55,
        (55, 60): set_male_55_60,
        (60, 65): set_male_60_65,
        (65, 70): set_male_65_70,
        (70, 75): set_male_70_75,
        (75, 80): set_male_75_80,
        (80, 85): set_male_80_85,
        (85, 90): set_male_85_90,
        (90, 95): set_male_90_95,
        (95, 1000): set_male_95_100,
    }
    plans_cut_male = {
        (50, 55): cut_male_50_55,
        (55, 60): cut_male_55_60,
        (60, 65): cut_male_60_65,
        (65, 70): cut_male_65_70,
        (70, 75): cut_male_70_75,
        (75, 80): cut_male_75_80,
        (80, 85): cut_male_80_85,
        (85, 90): cut_male_85_90,
        (90, 955): cut_male_90_95,
    }
    plans_set_female = {
        (50, 55): set_female_50_55,
        (55, 60): set_female_55_60,
        (60, 65): set_female_60_65,
        (65, 70): set_female_65_70,
        (70, 75): set_female_70_75,
        (75, 80): set_female_75_80,
        (80, 85): set_female_80_85,
        (85, 90): set_female_85_90,
        (90, 95): set_female_90_95,
        (95, 1000): set_female_95_100,
    }
    plans_cut_female = {
        (50, 55): cut_female_50_55,
        (55, 60): cut_female_55_60,
        (60, 65): cut_female_60_65,
        (65, 70): cut_female_65_70,
        (70, 75): cut_female_70_75,
        (75, 80): cut_female_75_80,
        (80, 855): cut_female_80_85,
    }
    # Поиск плана питания в зависимости от веса
    if gender == 'male' and goal == 'Набор':
        for (min_weight, max_weight), plan in plans_set_male.items():
            if min_weight <= weight < max_weight:
                return f"Цель: {goal}. План питания: {plan}"
    if gender == 'male' and goal == 'Сушка':
        for (min_weight, max_weight), plan in plans_cut_male.items():
            if min_weight <= weight < max_weight:
                return f"Цель: {goal}. План питания: {plan}"
    if gender == 'female' and goal == 'Набор':
        for (min_weight, max_weight), plan in plans_set_female.items():
            if min_weight <= weight < max_weight:
                return f"Цель: {goal}. План питания: {plan}"
    if gender == 'female' and goal == 'Сушка':
        for (min_weight, max_weight), plan in plans_cut_female.items():
            if min_weight <= weight < max_weight:
                return f"Цель: {goal}. План питания: {plan}"
    return "План не найден для данного веса."

@bot.message_handler(commands=['start'])
def start_message(message):
    print(f"Пользователь {message.chat.id} запустил бота")
    markup = types.InlineKeyboardMarkup()
    male_button = types.InlineKeyboardButton("Мужчина", callback_data='male')
    female_button = types.InlineKeyboardButton("Женщина", callback_data='female')
    markup.add(male_button, female_button)
    bot.send_message(message.chat.id, "Вас приветствует бот по планированию питания и тренировок Подтянис-МИСИС. Просим учесть, если у вас есть любые отклонения от норм здоровья, то наша программа вам противопоказана", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_gender_selection(call):
    if call.data == 'male':
        user_data[call.message.chat.id] = {'gender': 'male'}
        ask_weight(call.message)
    elif call.data == 'female':
        user_data[call.message.chat.id] = {'gender': 'female'}
        ask_weight(call.message)
    elif call.data in ['weight_set', 'cutting']:
        user_data[call.message.chat.id]['goal'] = 'Набор' if call.data == 'weight_set' else 'Сушка'
        choose_plan(call.message)
    elif call.data == 'food_plan':
        show_nutrition_plan(call.message)
    elif call.data == 'training_plan' and user_data[call.message.chat.id]['gender'] == 'male':
        if user_data[call.message.chat.id]['goal'] == 'Набор':
            show_male_set_training_plan(call.message)
        else:
            show_male_cut_training_plan(call.message)
    elif call.data == 'training_plan' and user_data[call.message.chat.id]['gender'] == 'female':
        if user_data[call.message.chat.id]['goal'] == 'Набор':
            show_female_set_training_plan(call.message)
        else:
            show_female_cut_training_plan(call.message)
    elif call.data == 'back_to_plan':
        choose_plan(call.message)
    elif call.data == 'back_to_imt':
        show_imt_recommendations(call.message)


def ask_weight(message):
    msg = bot.send_message(message.chat.id, "Введите свой вес в кг:")
    bot.register_next_step_handler(msg, process_weight_step)

def process_weight_step(message):
    try:
        weight = float(message.text)
        user_data[message.chat.id]['weight'] = weight
        ask_height(message)
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите вес числом.")
        ask_weight(message)

def ask_height(message):
    msg = bot.send_message(message.chat.id, "Введите свой рост в м:")
    bot.register_next_step_handler(msg, process_height_step)

def process_height_step(message):
    try:
        height = float(message.text)
        user_data[message.chat.id]['height'] = height
        show_imt_recommendations(message)
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите рост числом.")
        ask_height(message)

def show_imt_recommendations(message):
    gender = user_data[message.chat.id]['gender']
    weight = user_data[message.chat.id]['weight']
    height = user_data[message.chat.id]['height']
    imt = weight / (height) ** 2

    if imt < 18.5:
        recommendation = "Недостаток массы тела."
    elif 18.5 <= imt < 24.9:
        recommendation = "Норма массы тела."
    elif 25 <= imt < 29.9:
        recommendation = "Избыточная масса тела."
    else:
        recommendation = "Высокий избыток массы тела."

    markup = types.InlineKeyboardMarkup()
    set_button = types.InlineKeyboardButton("Набор", callback_data='weight_set')
    cut_button = types.InlineKeyboardButton("Сушка", callback_data='cutting')
    markup.add(set_button, cut_button)
    bot.send_message(message.chat.id,
                     f"""Ваш ИМТ: {imt:.1f}. {recommendation}
P.S Основываясь только на таких данных, мы не можем судить о вашей физической форме, поэтому таблица лишь примерная, для каждого человека значение ИМТ не отражает полноты картины, поэтому выбор плана тренировок и питания остается только за вами.
Выберите цель:""", reply_markup=markup)


def choose_plan(message):
    weight = user_data[message.chat.id]['weight']
    goal = user_data[message.chat.id].get('goal')  # Получаем цель из данных пользователя
    markup = types.InlineKeyboardMarkup()
    food_button = types.InlineKeyboardButton("Питание", callback_data='food_plan')
    train_button = types.InlineKeyboardButton("Тренировки", callback_data='training_plan')
    back_button = types.InlineKeyboardButton("Назад", callback_data='back_to_imt')
    markup.add(food_button, train_button)
    markup.add(back_button)
    bot.send_message(message.chat.id, "Выберите необходимый план", reply_markup=markup)


def show_nutrition_plan(message):
    weight = user_data[message.chat.id]['weight']
    goal = user_data[message.chat.id].get('goal')  # Получаем цель из данных пользователя
    nutrition_plan = get_nutrition_plan(weight, goal, user_data[message.chat.id]['gender'])
    markup = types.InlineKeyboardMarkup()
    back_button = types.InlineKeyboardButton("Назад", callback_data='back_to_plan')
    markup.add(back_button)
    bot.send_message(message.chat.id, f"{nutrition_plan}", reply_markup=markup)



def show_female_set_training_plan(message):
    markup = types.InlineKeyboardMarkup()
    back_button = types.InlineKeyboardButton("Назад", callback_data='back_to_plan')
    markup.add(back_button)
    bot.send_message(message.chat.id, "https://telegra.ph/Podtyanis-misis-11-25", reply_markup=markup)

def show_female_cut_training_plan(message):
    markup = types.InlineKeyboardMarkup()
    back_button = types.InlineKeyboardButton("Назад", callback_data='back_to_plan')
    markup.add(back_button)
    bot.send_message(message.chat.id, "https://telegra.ph/Trenirovka-zhenskaya-sushka-11-27", reply_markup=markup)

def show_male_set_training_plan(message):
    markup = types.InlineKeyboardMarkup()
    back_button = types.InlineKeyboardButton("Назад", callback_data='back_to_plan')
    markup.add(back_button)
    bot.send_message(message.chat.id, "https://telegra.ph/Programmy-trenirovok-dlya-nabora-myshechnoj-massy-muzhchinam-11-24", reply_markup=markup)

def show_male_cut_training_plan(message):
    markup = types.InlineKeyboardMarkup()
    back_button = types.InlineKeyboardButton("Назад", callback_data='back_to_plan')
    markup.add(back_button)
    bot.send_message(message.chat.id, "https://telegra.ph/Programma-trenirovok-dlya-sushki-muzhchinam-11-27", reply_markup=markup)    

bot.polling(none_stop=True)
