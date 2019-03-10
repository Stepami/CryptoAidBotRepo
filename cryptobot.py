# -*- coding: utf-8 -*-
import sqlite3
import telebot
import os
import BotsConfig
from selenium import webdriver
from telebot.types import LabeledPrice
from datetime import timedelta, date

bot = telebot.TeleBot(BotsConfig.token, threaded = False)

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--no-sandbox')

@bot.message_handler(commands=["start"])
def init_client(message):
    uid = message.chat.id
    user = message.from_user
    connection = sqlite3.connect(BotsConfig.db_connection)
    cursor = connection.cursor()
    cursor.execute("SELECT username FROM UserInfoTable WHERE userid = :uid", {"uid": uid})
    query_result = cursor.fetchone()
    if query_result == None:
        cursor.execute("""
        INSERT INTO UserInfoTable
        (userid, username, firstname, lastname)
        VALUES(?, ?, ?, ?)
        """, (uid, user.username, user.first_name, user.last_name))
        connection.commit()
        bot.send_message(uid, "Приветствую, " + user.username + "!")
    else:
        if query_result[0] != user.username:
            cursor.execute("""
            UPDATE UserInfoTable
            SET username = :uname
            WHERE userid = :uid
            """, {"uname" : user.username, "uid" : uid})
            connection.commit()
            bot.send_message(uid, "Давно не виделись, " + user.username + "!")
        else:
            bot.send_message(uid, "Давно не виделись, " + query_result[0] + "!")
    connection.close()

@bot.message_handler(commands=["help"])
def show_command_list(message):
    temp = ""
    for i in range(0, BotsConfig.help_size):
        temp += BotsConfig.help[i]
        temp += "\n"
    bot.send_message(message.chat.id,temp)

@bot.message_handler(commands=["analytics"])
def show_analytics(message):
    uid = message.chat.id
    if not IsSubscribed(uid, BotsConfig.db_connection):
        BuySubscription(uid)
    else:
        connection = sqlite3.connect(BotsConfig.db_connection)
        cursor = connection.cursor()
        cursor.execute("SELECT cryptocurrency FROM UserInfoTable WHERE userid = :uid", {"uid" : uid})
        temp = cursor.fetchone()[0]
        if temp == None:
            bot.send_message(uid, "Вы не выбрали криптовалюту")
        else:
            cursor.execute("SELECT :curr_an_txt FROM AdminTable WHERE id = 1", {"curr" : temp})
            bot.send_message(uid, cursor.fetchone()[0])
        connection.close()

@bot.message_handler(commands=["setcryptocurrency"])
def set_cryptocurrency(message):
    uid = message.chat.id
    if not IsSubscribed(uid, BotsConfig.db_connection):
        BuySubscription(uid)
    else:
        temp = ""
        connection = sqlite3.connect(BotsConfig.db_connection)
        cursor = connection.cursor()
        currencies = ["btc","bch","ltc","zec","sc"]
        try:
            temp = message.text.split(' ')[1]
        except IndexError:
            bot.send_message(uid, "Вы не ввели валюту")
            return
        if temp not in currencies:
            bot.send_message(uid, "Вы неправильно ввели валюту")
        else:
            cursor.execute("""
            UPDATE UserInfoTable
            SET cryptocurrency = :curr
            WHERE userid = :uid
            """, {"curr" : temp, "uid" : uid})
            connection.commit()
            bot.send_message(uid, "Вы успешно выбрали криптовалюту " + temp)
        connection.close()

@bot.message_handler(commands=["course"])
def show_course(message):
    uid = message.chat.id
    if not IsSubscribed(uid, BotsConfig.db_connection):
        BuySubscription(uid)
    else:
        bot.send_message(uid, "Подождите немного")
        connection = sqlite3.connect(BotsConfig.db_connection)
        cursor = connection.cursor()
        cursor.execute("SELECT cryptocurrency FROM UserInfoTable WHERE userid = :uid", {"uid" : uid})
        temp = cursor.fetchone()[0]
        if temp == None:
            bot.send_message(uid, "Вы не выбрали криптовалюту")
        else:
            driver = webdriver.Chrome(chrome_options = options)
            driver.set_window_size(1280, 720)
            driver.get(BotsConfig.url.format(temp))
            driver.save_screenshot(BotsConfig.course_photo_path)
            bot.send_photo(uid, photo = open(BotsConfig.course_photo_path, "rb"))
            driver.quit()
            os.remove(BotsConfig.course_photo_path)
        connection.close()

def IsSubscribed(uid: int, db_connection: str):
    connection = sqlite3.connect(db_connection)
    cursor = connection.cursor()
    cursor.execute("SELECT subdate FROM UserInfoTable WHERE userid = :uid", {"uid" : uid})
    temp = cursor.fetchone()[0]
    connection.close()
    if temp == None:
        return False
    else:
        return((date.today() - date(int(temp.split("-")[0]), int(temp.split("-")[1]), int(temp.split("-")[2]))).days <= 30)

def BuySubscription(uid: int):
	bot.send_message(uid, "Ваша подписка истекла или вы её не приобретали.\nДля полчения доступа к функционалу бота необходимо купить подписку")
	bot.send_invoice(uid, title = 'Подписка',
                     description = '30-дневная подписка на бота',
                     provider_token = BotsConfig.provider_token,
                     currency = 'rub',
                     prices = [LabeledPrice(label='Доступ к функционалу бота', amount=1000)],
                     start_parameter = 'bot-subscription',
                     invoice_payload = 'subscription payload')

@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                  error_message="Aliens tried to steal your card's CVV, but we successfully protected your credentials,"
                                                " try to pay again in a few minutes, we need a small rest.")

@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    uid = message.chat.id
    subdate = str(date.today().year) + "-" + str(date.today().month) + "-" + str(date.today().day)
    connection = sqlite3.connect(db_connection)
    cursor = connection.cursor()
    cursor.execute("""
    UPDATE UserInfoTable
    SET subdate = :subdate
    WHERE userid = :uid
    """, {"subdate" : subdate, "uid" : uid})
    connection.commit()
    connection.close()
    bot.send_message(uid, "Подписка успешно приобретена!")

if __name__ == '__main__':
    bot.infinity_polling()
