import telebot
import requests
import random
import string
from telebot import types

length = 12
users = {}
server_url = 'https://xnet-server.onrender.com'

headers = {'Accept': 'application/json'}


markup = types.ReplyKeyboardMarkup(row_width=1,resize_keyboard=True)
itembtn1 = types.InlineKeyboardButton('Удалить', callback_data='Delete')
itembtn2 = types.InlineKeyboardButton('Отмена', callback_data='Cancel')
markup.add(itembtn1, itembtn2)

class User:
    def __init__(self, name):
        self.name = name
        self.age = None
        self.firstname = None


bot = telebot.TeleBot("6206026868:AAFj5a88DMMwQMCf_4irVsc4LQ4Ybr6M9sM", parse_mode=None) # You can set parse_mode by default. HTML or MARKDOWN

@bot.message_handler(commands=['start'])
def send_welcome(message):
	bot.reply_to(message, "Привет в MagicDocs!")
        
@bot.message_handler(commands=['delete'])
def send_welcome(message):
    r = requests.get(server_url + '/findid?chatID=' + str(message.chat.id), headers=headers)

    if r.status_code != 404:
        bot.send_message(message.chat.id, 'Ты уверен что хочешь удалить профиль? ',reply_markup=markup)
    else: 
        bot.send_message(message.chat.id, 'У тебя нет профиля. Используй /generate')


@bot.message_handler(commands=['generate'])
def generate_welcome(message):
    
    headers = {'Accept': 'application/json'}
    r = requests.get(server_url + '/findid?chatID=' + str(message.chat.id), headers=headers)

    if r.status_code != 404:
        bot.reply_to(message, 'У тебя уже есть профиль. Напиши /delete, если хочешь пересоздать')

    else:
        msg = bot.reply_to(message, 'Напиши желаемое ФИО (по украински)')
        bot.register_next_step_handler(msg, process_name_step)

def process_name_step(message):
    try:
        chat_id = message.chat.id
        name = message.text
        user = User(name)
        users[chat_id] = user

        msg = bot.reply_to(message, 'Напиши желаемую дату рождения в формате ДД.ММ.ГГГГ')
        bot.register_next_step_handler(msg, process_age_step)

    except Exception as e:
         bot.reply_to(message,'Sorry... Something went wrong.')

def process_age_step(message):
    try:
        chat_id = message.chat.id
        age = message.text
        user = users[chat_id]
        user.age = age

        lower = string.ascii_lowercase
        upper = string.ascii_uppercase
        num = string.digits
        all = lower + upper + num 

        sss = "".join(random.sample(all,length))

        msg = bot.reply_to(message, 'Ok! ' + user.name + 'Age: ' + user.age + 'Id: ' + sss)
        
        r = requests.post('https://xnet-server.onrender.com/post', json={"id": sss, "name": user.name, "birthdate": user.age, "passport_id": 13131313, "firstname": "Oleksandr", "chatID": "" + str(msg.chat.id)})
    except Exception as e:
        bot.reply_to(message, 'oooops')



# r = requests.get('http://127.0.0.1:3132/delete?chatID=' + str(query.chat.id), headers=headers)


bot.enable_save_next_step_handlers(delay=2)
bot.infinity_polling()