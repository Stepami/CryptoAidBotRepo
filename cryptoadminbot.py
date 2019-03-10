# -*- coding: utf-8 -*-
import telebot
import sqlite3
import BotsConfig
from datetime import timedelta, date

admin_bot = telebot.TeleBot(BotsConfig.admin_token, threaded = False)

@admin_bot.message_handler(commands=["start"])
def init_admin(message):
    uid = message.chat.id
    if not IsAdmin(uid):
        admin_bot.send_message(uid, "Вы не админ!")
    else:
        admin_bot.send_message(uid, "Приветствую администрацию CryptoAidBot!")

@admin_bot.message_handler(commands=["help"])
def show_admin_command_list(message):
    temp = ""
    for i in range(0, BotsConfig.admin_help_size):
        temp += BotsConfig.admin_help[i]
        temp += "\n"
    admin_bot.send_message(message.chat.id, temp)

@admin_bot.message_handler(commands=["setanalyt"])
def setanalytics(message):
    uid = message.chat.id
    if not IsAdmin(uid):
        admin_bot.send_message(uid, "Вы не админ!")
    else:
        temp1 = ""
        temp2 = ""
        connection = sqlite3.connect(BotsConfig.db_connection)
        cursor = connection.cursor()
        currencies = ["btc","bch","ltc","zec","sc"]
        try:
            temp1 = message.text.split("\|/")[1]
        except IndexError:
            admin_bot.send_message(uid, "Вы не ввели валюту")
            return
        try:
            temp2 = message.text.split("\|/")[2]
        except IndexError:
            admin_bot.send_message(uid, "Вы не ввели текст аналитики!")
            return
        if temp1 not in currencies:
            admin_bot.send_message(uid, "Вы неправильно ввели валюту")
        else:
            cursor.execute("""
            UPDATE AdminTable
            SET :curr_an_txt = :atext
            WHERE id = 1
            """, {"curr" : temp1, "atext" : temp2})
            connection.commit()
            admin_bot.send_message(uid, "Вы успешно обновили аналитику!")
        connection.close()

@admin_bot.message_handler(commands=["join"])
def get_access(message):
    uid = message.chat.id
    subdate = str(date.today().year) + "-" + str(date.today().month) + "-" + str(date.today().day)
    if not IsAdmin(uid):
        admin_bot.send_message(uid, "Вы не админ!")
    else:
        connection = sqlite3.connect(BotsConfig.db_connection)
        cursor = connection.cursor()
        temp = ""
        try:
            temp = int(message.text.split(' ')[1])
            cursor.execute("""
            UPDATE UserInfoTable
            SET subdate = :subdate
            WHERE userid = :cid
            """, {"subdate" : subdate, "cid" : temp})
            connection.commit()
            admin_bot.send_message(uid, "Вы успешно подключили клиента!")
        except IndexError:
            admin_bot.send_message(uid, "Вы не ввели id!")
            return
        except ValueError:
            admin_bot.send_message(uid, "Вы ввели не id!")
            return
        connection.close()

@admin_bot.message_handler(commands=["detach"])
def deny_access(message):
    uid = message.chat.id
    if not IsAdmin(uid):
        admin_bot.send_message(uid, "Вы не админ!")
    else:
        connection = sqlite3.connect(BotsConfig.db_connection)
        cursor = connection.cursor()
        temp = ""
        try:
            temp = int(message.text.split(' ')[1])
            cursor.execute("""
            UPDATE UserInfoTable
            SET subdate = null
            WHERE userid = :cid
            """, {"cid" : temp})
            connection.commit()
            admin_bot.send_message(uid, "Вы успешно отключили клиента!")
        except IndexError:
            admin_bot.send_message(uid, "Вы не ввели id!")
            return
        except ValueError:
            admin_bot.send_message(uid, "Вы ввели не id!")
            return
        connection.close()
        
@admin_bot.message_handler(commands=["clientsinfo"])
def get_clients_info(message):
    uid = message.chat.id
    if not IsAdmin(uid):
        admin_bot.send_message(uid, "Вы не админ!")
    else:
        connection = sqlite3.connect(BotsConfig.db_connection)
        cursor = connection.cursor()
        cursor.execute("SELECT userid, username, firstname, lastname, subdate, cryptocurrency FROM UserInfoTable")
        clients = cursor.fetchall()
        connection.close()
        temp = "userid: {c[0]}\nusername: {c[1]}\nимя: {c[2]}\nфамилия: {c[3]}\nдата подписки: {c[4]}\nкриптовалюта: {c[5]}"
        for client in clients:
            if client[4] == None:
                admin_bot.send_message(uid, temp.format(c = client) + "\nПодписка неактивна")
            elif (date.today() - date(int(client[4].split("-")[0]), int(client[4].split("-")[1]), int(client[4].split("-")[2]))).days <= 30:
                admin_bot.send_message(uid, temp.format(c = client) + "\nПодписка активна")
            else:
                admin_bot.send_message(uid, temp.format(c = client) + "\nПодписка неактивна")

def IsAdmin(uid: int):
    return uid == 448967581

if __name__ == '__main__':
    admin_bot.infinity_polling()
