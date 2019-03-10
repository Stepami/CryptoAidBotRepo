# -*- coding: utf-8 -*-
token = "cryptobot_token"

admin_token = "cryptoadminbot_token"

provider_token = "provider_token"#yandex.kassa test

db_connection = "/root/cryptobotdir/cryptobotdatabase/py_crypto_bot_info.db"

course_photo_path = "course_photo.png"

url = "https://www.cryptocompare.com/coins/{0}/overview/USD"

help = [
    "start - Запуск бота",
    "help - Список доступных команд с их описанием",
    "analytics - Получение инфо-статей по выбранной криптовалюте",
    "setcryptocurrency - выбор криптовалюты. Доступно: btc(bitcoin), bch(bitcoin cash), ltc(litecoin), zec(zcash), sc(siacoin)",
    "course - получение курса выбранной криптовалюты"
    ]

help_size = len(help)

admin_help = [
    "start - Запуск бота",
    "help - Список команд и их описание",
    "setanalyt - Пример: /setanalyt\|/btc\|/example text"
    "join - Подключение клиента к боту по его ID.Поместить ID необходимо через пробел. Пример: /join 228322420",
    "detach - Отключение клиента от бота по его ID.Поместить ID необходимо через пробел. Пример: /detach 228322420",
    "clientsinfo - Получение информации о клиентах"
    ]

admin_help_size = len(admin_help)
