import telebot
from telebot import types
import config
import sqlite3
import os
import shutil

bot = telebot.TeleBot(config.token)


def scan_skins():
    files = os.listdir('skins/')
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    for file in files:
        f = file.strip('.png.gif').split('_')
        cursor.execute("INSERT INTO skins (path, name, description, author) VALUES (?, ?, ?, ?)", (file, f[0], f[1], f[2]))
    conn.commit()
    cursor.close()
    conn.close()
    print('Skins scanned!')


def send_skin(message, skin_id: int):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute("""SELECT name, path,  description, author FROM skins WHERE id = ?""", (skin_id,))
    skin = cursor.fetchone()
    cursor.close()
    conn.close()
    if skin is None:
        bot.send_message(message.chat.id, 'Skin not found!')
        return
    photo = open(f'skins/{skin[1]}', 'rb')
    keyboard = types.InlineKeyboardMarkup()
    key_prev = types.InlineKeyboardButton(text='Previous', callback_data=f'prev_{skin_id}')
    key_next = types.InlineKeyboardButton(text='Next', callback_data=f'next_{skin_id}')
    keyboard.add(key_prev, key_next)
    bot.send_document(message.chat.id, photo, caption=f'Name: {skin[0]}\nDescription: {skin[2]}\nAuthor: {skin[3]}', reply_markup=keyboard)


def init_db():
    if os.path.exists("db.sqlite3"):
        os.remove("db.sqlite3")
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS skins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT,
        name TEXT,
        description TEXT,
        author TEXT
    )""")
    cursor.close()
    conn.close()


def refresh():
    init_db()
    scan_skins()


def remove(message, skin_id: int):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute("""SELECT path FROM skins WHERE id = ?""", (skin_id,))
    skin = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    if skin is None:
        bot.send_message(message.chat.id, 'Skin not found!')
        return
    os.remove(f'skins/{skin[0]}')
    refresh()
    bot.send_message(message.chat.id, 'Skin removed!')


def get_file(message, file_type):
    try:
        file_id = message.document.file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        m = message.caption.replace(' ', '-').split('|')
        with open(f'new_skins/{m[0]}_{m[1]}_{m[2]}.{file_type}', 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.send_message(message.chat.id, 'Skin added! Wait for admin to approve it!')
    except:
        bot.send_message(message.chat.id, 'Something went wrong! Try again!')


def init():
    init_db()
    scan_skins()
    print('Init done!')
    bot.polling(non_stop=True, interval=0)


@bot.message_handler(commands=["list"])
def list_skins(message):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute("""SELECT id, name, description, author FROM skins""")
    skins = cursor.fetchall()
    cursor.close()
    conn.close()
    resp = 'All skins:\n'
    for skin in skins:
        resp += f'{skin[0]}. Name: {skin[1]}. Description: {skin[2]}. Author: {skin[3]}\n'
    bot.send_message(message.chat.id, resp)


@bot.message_handler(commands=["credits"])
def credits(message):
    bot.send_message(message.chat.id, 'Coming soon!')


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, f'Hello, {message.from_user.first_name}! I am a bot that can help you to choose AMOGUS skin for you!\nIt is strongly recommended to disable autosave media🙃')
    bot.send_message(message.chat.id, '© Mootfrost 2022')


@bot.message_handler(content_types=["text"])
def text(message):
    if message.text == '/skin':
        bot.send_message(message.chat.id, 'Send this command with skin id! Example: /skin 1 ')
    elif '/skin' in message.text:
        skin_id = int(message.text.split(' ')[1])
        send_skin(message, skin_id)
    elif '/remove' in message.text:
        try:
            password = message.text.split(' ')[2]
            if password == config.admin_pass:
                remove(message, int(message.text.split(' ')[1]))
            else:
                bot.send_message(message.chat.id, 'Wrong password!')
        except IndexError:
            bot.send_message(message.chat.id, 'You need to send password!')
    elif '/help' in message.text:
        bot.send_message(message.chat.id, 'Commands:\n'
                                          '/skin <id> - get skin by id\n'
                                          '/help - show this message\n'
                                          '/list - show all skins\n'
                                          'You can also send a photo(!!!WARNING DO NOT SELECT FILE COMPRESSION WHEN SEND!!!) with caption: <name>|<description>|<author>')
    elif '/refresh' in message.text:
        try:
            password = message.text.split(' ')[1]
            if password == config.admin_pass:
                refresh()
                bot.send_message(message.chat.id, 'Skins refreshed!')
            else:
                bot.send_message(message.chat.id, 'Wrong password!')
        except IndexError:
            bot.send_message(message.chat.id, 'You need to send password!')
    elif '/approve-all' in message.text:
        try:
            password = message.text.split(' ')[1]
            if password == config.admin_pass:
                files = os.listdir('new_skins/')
                for f in files:
                    shutil.move('new_skins/' + f, 'skins/')
                refresh()
                bot.send_message(message.chat.id, 'All skins approved and refreshed!')
            else:
                bot.send_message(message.chat.id, 'Wrong password!')
        except IndexError:
            bot.send_message(message.chat.id, 'You need to send password!')
    else:
        bot.send_message(message.chat.id, 'Unknown command! Use /help to get additional info.')


@bot.message_handler(content_types=["document"])
def photo(message):
    get_file(message, 'png')


@bot.message_handler(content_types=["animation"])
def gif(message):
    get_file(message, 'gif')


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if 'next' in call.data:
        send_skin(call.message, int(call.data.split('_')[1]) + 1)
    elif 'prev' in call.data:
        send_skin(call.message, int(call.data.split('_')[1]) - 1)


init()
