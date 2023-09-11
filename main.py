import telebot
import requests
import random
import string
from telebot import formatting

token = "6633313428:AAHB_bBOpF1FkXnznKemFjUqNpBbKP0m4rU"
length = 12
users = {}
server_url = 'https://xnet-server.onrender.com' # IP или URL сервера (xnet-server) # server_url = 'http://127.0.0.1:3132'
client_url = 'https://juliphy.github.io/project-x'

headers = {'Accept': 'application/json'}

# options = []


# markup = types.ReplyKeyboardMarkup(row_width=2)
# itembtn1 = types.InlineKeyboardButton('Удалить', callback_data='Delete')
# itembtn2 = types.InlineKeyboardButton('Отмена', callback_data='Cancel')
# markup.add(itembtn1, itembtn2)

class User:
    def __init__(self):
        self.name = None
        self.birthdate = None
        self.firstname = None
        self.url_face = None
        self.url_sign = None

user = User()

bot = telebot.TeleBot(token, parse_mode='HTML') # You can set parse_mode by default. HTML or MARKDOWN

def get_image_link(message):
    response_dict = message.json
    photo_array = response_dict.get('photo') 
    photo_dict = photo_array[1]
    file_id = photo_dict.get('file_id')

    print('BEFORE GET_FILE_URL')
    link = bot.get_file_url(file_id)

    x = requests.post('https://api.imgbb.com/1/upload?key=97d3e8374f244aac180e2a5f4727a8b8&image=' + link)
    response = x.json()
    print('BEFORE ASSIGNMENT END.')
    response_data = response['data']
    url = response_data['url']

    return url
    # bot.send_message(message.chat.id, 'https://api.telegram.org/file/bot' + token + '/' + file_id)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id,
                     formatting.format_text('Hello',formatting.hcode('User'), separator=' ')
    )
    
        
@bot.message_handler(commands=['delete'])
def delete_handler(message):
    r = requests.get(server_url + '/tele?chatID=' + str(message.chat.id), headers=headers)

    if r.status_code == 200:
        r = requests.get(server_url + '/delete?chatID=' + str(message.chat.id), headers=headers)
        bot.reply_to(message, 'Удалено')
    elif r.status_code == 404: 
        bot.reply_to(message, 'У тебя нет профиля. Создаем...')
        generate_handler(message)
    else:
        bot.send_message(message.chat.id, 'Что-то сломалось :(')
                

@bot.message_handler(commands=['info'])
def info_handler(message):
    r = requests.get(server_url + '/tele?chatID=' + str(message.chat.id), headers=headers)

    if r.status_code == 200:
        response_dict = r.json()
        bot.send_message(message.chat.id,
                        'Имя: ' + response_dict['name'] + '\nДата: ' + response_dict['birthdate'] + '\nID: ' + formatting.hcode(response_dict['id']) + '\nСайт для входа: ' + client_url)

    else:
        bot.send_message(message.chat.id, 'У тебя нет профиля. Создаем...')
        generate_handler(message)


@bot.message_handler(commands=['generate'])
def generate_handler(message):
    try:
        headers = {'Accept': 'application/json'}
        r = requests.get(server_url + '/tele?chatID=' + str(message.chat.id),headers=headers)

        if (r.status_code == 200):
            bot.reply_to(message, 'У тебя уже есть профиль. Напиши /delete, если хочешь пересоздать')
        else:
            msg = bot.reply_to(message, 'Напиши желаемое ФИО (по украински)')
            bot.register_next_step_handler(msg, process_name_step)
    except:
        bot.send_message(message.chat.id, 'Не возможно подключится к серверу!')

def process_name_step(message):
    try:
        vname = message.text
        user.name = vname
        firstname_array = user.name.split()

        if len(firstname_array) != 3:
            bot.send_message(message.chat.id, 'Ты написал неверное ФИО. Напиши правильно ФИО')
            generate_handler(message)
        else:
            msg = bot.reply_to(message, 'Напиши желаемую дату рождения в формате ДД.ММ.ГГГГ')
            bot.register_next_step_handler(msg, process_age_step)

    except Exception as e:
         bot.reply_to(message,'Sorry... Something went wrong.')

def process_age_step(message):
    try:
        print('AFTER')
        user.birthdate = message.text
    
        firstname_array = user.name.split()
        user.firstname = firstname_array[1]

        print('BEFORE 3X4')

        msg = bot.send_message(message.chat.id, 'Отправь фотографию 3x4;'+ formatting.hitalic('Некоректная') + 'фотография может остановить доступ к сайту.')
        bot.register_next_step_handler(msg, process_face_image_step)
    except Exception as err:
        print('Process AGESTEP WENT WRONG',err)

def process_face_image_step(message):
    try:
        print('BEFORE GET IMGAE')

        user.url_face = get_image_link(message)

        msg = bot.send_message(message.chat.id, 'Отправь фотографию твоей подписи примерно 270 на 110 пикселей. ;'+ formatting.hitalic('Некоректная') + 'фотография подпись может остановить доступ к сайту.')
        bot.register_next_step_handler(msg, process_sign_image_step)
    except Exception as e:
        print(e, 'ERROR')


def process_sign_image_step(message):
    try:
        user.url_sign = get_image_link(message)

        lower = string.ascii_lowercase
        upper = string.ascii_uppercase
        num = string.digits
        all = lower + upper + num

        sss = "".join(random.sample(all,12))

        bot.send_message(message.chat.id, 'Имя: ' + user.name + '\nДата: ' + user.birthdate + '\nID: ' + formatting.hcode(sss))
                
        requests.post('https://xnet-server.onrender.com/post', json={"id": sss, "name": user.name, "birthdate": user.birthdate, "passport_id": "1231231", "firstname": user.firstname, "chatID": str(message.chat.id), "kpp_id":'313132131', "urlFace": user.url_face, "urlSign": user.url_sign})

    except Exception as e:
        print(e, 'ERROR')


# r = requests.get('http://127.0.0.1:3132/delete?chatID=' + str(query.chat.id), headers=headers)


bot.enable_save_next_step_handlers(delay=2)
bot.infinity_polling()
