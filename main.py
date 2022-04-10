import telebot
import config
import sqlite3
import os

bot = telebot.TeleBot(config.token)


def scan_skins():
    files = os.listdir('skins/')
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    for file in files:
        f = file.strip('.png').split('_')
        cursor.execute("INSERT INTO skins (path, name, description, author) VALUES (?, ?, ?, ?)", (file, f[0], f[1], f[2]))
    conn.commit()
    cursor.close()
    conn.close()
    print('Skins scanned!')


def init():
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
    scan_skins()
    print('Init done!')
    bot.polling(non_stop=True, interval=0)
    print('Bot started!')


def send_skin(message, skin_id: int):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute("""SELECT name, path,  description, author FROM skins WHERE id = ?""", (skin_id,))
    skin = cursor.fetchone()
    cursor.close()
    conn.close()
    photo = open(f'skins/{skin[1]}', 'rb')
    bot.send_document(message.chat.id, photo, caption=f'Name: {skin[0]}\nDescription: {skin[2]}\nAuthor: {skin[3]}')


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
    bot.send_message(message.chat.id, f'Hello, {message.from_user.first_name}! I am a bot that can help you to choose AMOGUS skin for you!')
    bot.send_message(message.chat.id, '© Mootfrost 2022')


@bot.message_handler(content_types=["text"])
def text(message):
    if message.text == '/skin':
        bot.send_message(message.chat.id, 'Send this command with skin id! Example: /skin 1 ')
    elif '/skin' in message.text:
        skin_id = int(message.text.split(' ')[1])
        send_skin(message, skin_id)
    elif '/help' in message.text:
        bot.send_message(message.chat.id, 'Commands:\n'
                                          '/skin <id> - get skin by id\n'
                                          '/help - show this message\n'
                                          '/list - show all skins\n'
                                          'You can also send a photo(!!!WARNING DO NOT SELECT FILE COMPRESSION WHEN SEND!!!) with caption: <name>|<description>|<author>')
    else:
        bot.send_message(message.chat.id, 'Unknown command! Use /help to get additional info.')


@bot.message_handler(content_types=["document"])
def photo(message):
    try:
        print('Photo received!')
        print(message.caption)
        file_id = message.document.file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        m = message.caption.replace(' ', '-').split('|')
        with open(f'new_skins/{m[0]}_{m[1]}_{m[2]}.png', 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.send_message(message.chat.id, 'Skin added! Wait for admin to approve it!')
    except:
        bot.send_message(message.chat.id, 'Something went wrong! Try again!')


@bot.message_handler(content_types=["animation"])
def gif(message):
    bot.send_message(message.chat.id, 'GIF skins can be published later. Sorry for inconvenience.')


init()




