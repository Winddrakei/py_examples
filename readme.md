# Описание приложения

Для телеграм-бота использовано API Real-Time Product Search https://rapidapi.com/letscrape-6bRBa3QguO5/api/real-time-product-search (товары с интернет-площадок Amazon, eBay, Walmart, Best Buy, Target и др., собранные на в Google Products).

    Имя: SearchGoogleProducts
    Адрес: https://t.me/msqTestPyBot
    Бот: @msqTestPyBot

_Файл запуска бота - main.py_

Бот принимает команды:
/help - помощь по командам бота;
/low - вывод самых дешевых товаров поиска;
/high - вывод самых дорогих товаров поиска;
/custom - вывод товаров поиска в заданном ценовом диапазоне;
/history - вывод истории запросов пользователя (запросами считаются команды /low, /high и /custom);
/hello-world, /hello - приветствие;
/start - запуск/перезапуск бота.
Также бот отвечает приветствием на слово "привет" (в стартовом состоянии*).

    *Стартовое состояние - основное состояние: выведены командные кнопки, бот ожидает ввода команды

**Команда /low.** После ввода команды у пользователя запрашивается:
1. Название товара, по которому будет проводиться поиск;
2. Количество единиц товара, которое необходимо вывести (от 1 до 30).

**Команда /high.** После ввода команды у пользователя запрашивается:
1. Название товара, по которому будет проводиться поиск;
2. Количество единиц товара, которое необходимо вывести (от 1 до 30).

**Команда /custom.** После ввода команды у пользователя запрашивается:
1. Название товара, по которому будет проводиться поиск;
2. Диапазон значений выборки цены (например: 100-200);
3. Количество единиц товара, которое необходимо вывести (от 1 до 30).
    
**Команда /history.** После ввода команды выводится краткая история запросов пользователя (последние 10 запросов)

_Предельное количество результатов за один поиск: 30 наименований. Сервером API установлено ограничение на количество запросов: не более 1 в минуту._
