import sqlite3
import telebot
from telebot import types
from database import Database

db = Database('db.db')
bot = telebot.TeleBot("5035540250:AAGJKABHD0wsyNYHKTXhIUXwgIgbK_a_rdc")

class Database:
    def __init__(self, database_file):
        self.connection = sqlite3.connect(database_file, check_same_thread = False)
        self.cursor = self.connection.cursor()
    
    def add_queue(self, chat_id, gender): # Добавление новой очереди
        with self.connection:
            return self.cursor.execute("INSERT INTO `queue` (`chat_id`, `gender`) VALUES (?,?)", (chat_id, gender))
    
    def delete_queue(self, chat_id):
        with self.connection:
            return self.cursor.execute("DELETE FROM `queue` WHERE `chat_id` = ?", (chat_id,))
    
    def delete_chat(self, id_chat):
        with self.connection:
            return self.cursor.execute("DELETE FROM `chats` WHERE `id` = ?", (id_chat,))

    def set_gender(self, chat_id, gender):
        with self.connection:
            user = self.cursor.execute("SELECT * FROM `users` WHERE `chat_id` = ?", (chat_id,)).fetchmany(1)
            if bool(len(user)) == False:
                self.cursor.execute("INSERT INTO `users` (`chat_id`, `gender`) VALUES (?,?)", (chat_id, gender))
                return True
            else:
                return False

    def get_gender(self, chat_id):
        with self.connection:
            user = self.cursor.execute("SELECT * FROM `users` WHERE `chat_id` = ?", (chat_id,)).fetchmany(1)
            if bool(len(user)):
                for row in user:
                    return row[2]
            else:
                return False
    
    def get_gender_chat(self, gender):
        with self.connection:
            chat = self.cursor.execute("SELECT * FROM `queue` WHERE `gender` = ?", (gender,)).fetchmany(1)
            if bool(len(chat)):
                for row in chat:
                    user_info = [row[1], row[2]]
                    return user_info
            else:
                return [0]

    def get_chat(self):
        with self.connection:
            chat = self.cursor.execute("SELECT * FROM `queue`", ()).fetchmany(1)
            if bool(len(chat)):
                for row in chat:
                    user_info = [row[1], row[2]]
                    return user_info
            else:
                return [0]

    def create_chat(self, chat_one, chat_two):
        with self.connection:
            if chat_two != 0:
                # Создание чата
                self.cursor.execute("DELETE FROM `queue` WHERE `chat_id` = ?", (chat_two,))
                self.cursor.execute("INSERT INTO `chats` (`chat_one`, `chat_two`) VALUES (?,?)", (chat_one, chat_two,))
                return True

            else:
                # Становимся в очередь
                return False
    
    def get_active_chat(self, chat_id):
        with self.connection:
            chat = self.cursor.execute("SELECT * FROM `chats` WHERE `chat_one` = ?", (chat_id,))
            id_chat = 0
            for row in chat:
                id_chat = row[0]
                chat_info = [row[0], row[2]]
            
            if id_chat == 0:
                chat = self.cursor.execute("SELECT * FROM `chats` WHERE `chat_two` = ?", (chat_id,))
                for row in chat:
                    id_chat = row[0]
                    chat_info = [row[0], row[1]]
                if id_chat == 0:
                    return False
                else:
                    return chat_info
            else:
                return chat_info


def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
    item1 = types.KeyboardButton('👥 Поиск собеседника')
    markup.add(item1)
    return markup

def stop_dialog():
    markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
    item1 = types.KeyboardButton('🗣 Сказать свой профиль')
    item2 = types.KeyboardButton('/stop')
    markup.add(item1, item2)
    return markup

def stop_search():
    markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
    item1 = types.KeyboardButton('❌ Остановить поиск')
    markup.add(item1)
    return markup

@bot.message_handler(commands = ['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
    item1 = types.KeyboardButton('Я Парень 👨')
    item2 = types.KeyboardButton('Я Девушка 👩‍🦱')
    markup.add(item1, item2)

    bot.send_message(message.chat.id, 'Привет, {0.first_name}! Добро пожаловать в анонимный чат Кузнецка  ! Укажите ваш пол! '.format(message.from_user), reply_markup = markup)

@bot.message_handler(commands = ['menu'])
def menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
    item1 = types.KeyboardButton('👥 Поиск собеседника')
    markup.add(item1)

    bot.send_message(message.chat.id, '📝 Меню'.format(message.from_user), reply_markup = markup)

@bot.message_handler(commands = ['stop'])
def stop(message):
    chat_info = db.get_active_chat(message.chat.id)
    if chat_info != False:
        db.delete_chat(chat_info[0])
        markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
        item1 = types.KeyboardButton('✏️ Следующий диалог')
        item2 = types.KeyboardButton('/menu')
        markup.add(item1, item2)

        bot.send_message(chat_info[1], '❌ Собеседник покинул чат', reply_markup = markup)
        bot.send_message(message.chat.id, '❌ Вы вышли из чата', reply_markup = markup)
    else:
        bot.send_message(message.chat.id, '❌ Вы не начали чат!', reply_markup = markup)


@bot.message_handler(content_types = ['text'])
def bot_message(message):
    if message.chat.type == 'private':
        if message.text == '👥 Поиск собеседника' or message.text == '✏️ Следующий диалог':
            markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
            item1 = types.KeyboardButton('🔎 Парень')
            item2 = types.KeyboardButton('🔎 Девушка')
            item3 = types.KeyboardButton('👩‍👨 Рандом')
            markup.add(item1, item2, item3)

            bot.send_message(message.chat.id, 'Кого искать?', reply_markup = markup)

            
        elif message.text == '❌ Остановить поиск':
            db.delete_queue(message.chat.id)
            bot.send_message(message.chat.id, '❌ Поиск остановлен, напишите /menu', reply_markup = main_menu())

        
        elif message.text == '🔎 Парень':
            user_info = db.get_gender_chat('male')
            chat_two = user_info[0]
            if db.create_chat(message.chat.id, chat_two) == False:
                db.add_queue(message.chat.id, db.get_gender(message.chat.id))
                bot.send_message(message.chat.id, '👻 Поиск собеседника', reply_markup = stop_search())
            else:
                mess = 'Собеседник найден! Чтобы остановить диалог, напишите /stop'

                bot.send_message(message.chat.id, mess, reply_markup = stop_dialog())
                bot.send_message(chat_two, mess, reply_markup = stop_dialog())
        
        
        elif message.text == '🔎 Девушка':
            user_info = db.get_gender_chat('female')
            chat_two = user_info[0]
            if db.create_chat(message.chat.id, chat_two) == False:
                db.add_queue(message.chat.id, db.get_gender(message.chat.id))
                bot.send_message(message.chat.id, '👻 Поиск собеседника', reply_markup = stop_search())
            else:
                mess = 'Собеседник найден! Чтобы остановить диалог, напишите /stop'

                bot.send_message(message.chat.id, mess, reply_markup = stop_dialog())
                bot.send_message(chat_two, mess, reply_markup = stop_dialog())
        

        elif message.text == '👩‍👨 Рандом':
            user_info = db.get_chat()
            chat_two = user_info[0]

            if db.create_chat(message.chat.id, chat_two) == False:
                db.add_queue(message.chat.id, db.get_gender(message.chat.id))
                bot.send_message(message.chat.id, '👻 Поиск собеседника', reply_markup = stop_search())
            else:
                mess = 'Собеседник найден! Чтобы остановить диалог, напишите /stop'

                bot.send_message(message.chat.id, mess, reply_markup = stop_dialog())
                bot.send_message(chat_two, mess, reply_markup = stop_dialog())
        
        elif message.text == '🗣 Сказать свой профиль':
            chat_info = db.get_active_chat(message.chat.id)
            if chat_info != False:
                if message.from_user.username:
                    bot.send_message(chat_info[1], '@' + message.from_user.username)
                    bot.send_message(message.chat.id, '🗣 Вы сказали свой профиль')
                else:
                    bot.send_message(message.chat.id, '❌ В вашем аккаунте не указан username')
            else:
                bot.send_message(message.chat.id, '❌ Вы не начали диалог!')

        

        elif message.text == 'Я Парень 👨':
            if db.set_gender(message.chat.id, 'male'):
                bot.send_message(message.chat.id, '✅ Ваш пол успешно добавлен!', reply_markup = main_menu())
            else:
                bot.send_message(message.chat.id, '❌ Вы уже указали ваш пол. Пройдите меню /menu ')
        
        elif message.text == 'Я Девушка 👩‍🦱':
            if db.set_gender(message.chat.id, 'female'):
                bot.send_message(message.chat.id, '✅ Ваш пол успешно добавлен!', reply_markup = main_menu())
            else:
                bot.send_message(message.chat.id, '❌ Вы уже указали ваш пол. Пройдите меню /menu ')
        
        else:
            if db.get_active_chat(message.chat.id) != False:
                chat_info = db.get_active_chat(message.chat.id)
                bot.send_message(chat_info[1], message.text)
            else:
                bot.send_message(message.chat.id, '❌ Вы не начали диалог!')


@bot.message_handler(content_types='stickers')
def bot_stickers(message):
    if message.chat.type == 'private':
        chat_info = db.get_active_chat(message.chat.id)
        if chat_info != False:
            bot.send_sticker(chat_info[1], message.sticker.file_id)
        else:
            bot.send_message(message.chat.id, '❌ Вы не начали диалог!')

@bot.message_handler(content_types='voice')
def bot_voice(message):
    if message.chat.type == 'private':
        chat_info = db.get_active_chat(message.chat.id)
        if chat_info != False:
            bot.send_voice(chat_info[1], message.voice.file_id)
        else:
            bot.send_message(message.chat.id, '❌ Вы не начали диалог!')



bot.polling(none_stop = True)