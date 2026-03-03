import downloader
import config
import logging
import os
import telebot
from queue import Queue
import threading
import db_helper
import helper

API_TOKEN = config.TOKEN
admin_id = config.admin_id

bot = telebot.TeleBot(API_TOKEN)
task_queue = Queue()
user_data = {}
backup = {}
logging.basicConfig(level=logging.INFO, filename="downloader.log", filemode="a",
                    format="%(asctime)s %(levelname)s %(message)s")

pid = str(os.getpid())
pidfile = open("pidfile.pid", 'w')
pidfile.write(pid)
pidfile.close()


# Функция обработки видео
def process_video_task(chat_id, link, timestamp):
    try:
        clip = (link, timestamp)
        logging.info(clip)
        downloader.download_video(link, timestamp)

        with open("videos/output.mp4", "rb") as video_file:
            logging.info("starting video sending")
            bot.send_video(chat_id, video_file, caption="", timeout=100000)

        os.remove("videos/output.mp4")  # Удаляем файл после отправки
        db_helper.add_record(chat_id)
    except Exception as e:
        bot.send_message(chat_id,
                         f"Произошла ошибка. Проверьте правильность ввода данных и обратитесь к разработчику @codimka")
        logging.error(e)


# Фоновый поток для обработки очереди
def worker():
    while True:
        chat_id, link, timestamp = task_queue.get()
        process_video_task(chat_id, link, timestamp)
        task_queue.task_done()


# Запуск фонового потока
threading.Thread(target=worker, daemon=True).start()


# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_info = bot.get_chat(message.chat.id)
    username = str(user_info.username)
    name = str(user_info.first_name) + " " + str(user_info.last_name)
    db_helper.add_user(message.chat.id, username, name)
    bot.send_message(message.chat.id, "Привет! Я помогу вырезать фрагмент из видео Youtube. "
                                      "Сначала отправьте ссылку на видео")


# очистка словаря хранящего недавние действия
@bot.message_handler(commands=['cancel'])
def to_main_menu(message):
    user_data[message.chat.id] = {}
    bot.send_message(message.chat.id, "Отправьте ссылку на видео YouTube")


@bot.message_handler(commands=['download'])
def send_file(message):
    if message.chat.id == admin_id:
        print("получено")
        try:
            target = message.text.split()[1]
            if target == 'db':
                db = open("yt_database.db", "rb")
                bot.send_document(admin_id, db)
        except Exception as e:
            print(e)
            bot.send_message(admin_id, str(e))


# Обработка ссылки на видео
@bot.message_handler(func=lambda message: (message.chat.id in user_data and user_data[message.chat.id] == {})
                                          or message.chat.id not in user_data)
def get_video_link(message):
    if helper.is_youtube_link(message.text):
        title, author, preview_link = downloader.is_available(message.text)
        if title is not None:
            try:
                downloader.download_preview(preview_link, message.chat.id)
                preview_name = f"preview-{message.chat.id}.jpg"
                preview = open(preview_name, "rb")
                bot.send_photo(message.chat.id, preview, helper.text_preview(title, author), parse_mode="Markdown")
                preview.close()
                os.remove(preview_name)
                user_data[message.chat.id] = {'link': message.text, 'title': title, 'author': author}
            except Exception as e:
                print(e)
                logging.error(e)
                user_data[message.chat.id] = {}
                bot.send_message(message.chat.id, "❌Что-то пошло не так")
        else:
            bot.send_message(message.chat.id,
                             "❌Видео не найдено. Проверьте, правильно ли вы указали ссылку")
    else:
        bot.send_message(message.chat.id, "❌Отправьте ссылку в корректном формате")


# Обработка времени начала
@bot.message_handler(func=lambda message: message.chat.id in user_data and "start" not in user_data[message.chat.id])
def get_start_time(message):
    try:
        chat_id = message.chat.id
        backup = user_data[chat_id]
        timecodes = str(message.text).strip()
        # print(type(timecodes))
        start, end = timecodes.split('-')
        # print(start, end, type(start))
        start = helper.time_to_seconds(start)
        end = helper.time_to_seconds(end)
        if start < end and end - start <= 900:
            info = (chat_id, user_data[chat_id]["link"], timecodes)
            task_queue.put(info)
            logging.info(f"{chat_id}, {user_data[chat_id]['title']}, {user_data[chat_id]['author']}, "
                         f"{start}, {end}, {user_data[chat_id]['link']}")
            bot.send_message(message.chat.id, "Принято! Скоро пришлю видео")
            user_data[chat_id] = {}
        elif start > end:
            bot.send_message(message.chat.id, "Время начала должно быть меньше времени конца!")
        else:
            bot.send_message(message.chat.id, "Длительность отрывка должна быть не более 15 минут")
    except Exception as e:
        bot.send_message(message.chat.id, "Что-то пошло не так. Попробуйте ещё раз")
        logging.error(e)
        user_data[message.chat.id] = backup


# Запуск бота
#bot.start_polling(none_stop=True, non_stop=True)
bot.infinity_polling()
