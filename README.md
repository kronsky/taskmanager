# Выпускной проект школы Кодемика
## Тема 1: Taskmanager

Taskmanager в виде телеграм бота.
Проект запущен в докере на VPS сервере, имя бота в телеграм - **@kronsky_taskmanager_bot**

Бот построен на библиотеке pyTelegramBotAPI версии 4.5.1. Бот умеет создавать задачи и управлять ими. Начинать и завершать выполнение задач, учитывать время выполнения задачи, вести статистику. Бот уведомляет пользователя о сроках начала выполнения задач и просроке задач. Бот многопользовательский, для каждого пользователя создается отдельная таблица задач в базе данных.

При запуске основного main.py файла создаётся отдельный поток, в котором запускается notification.py для обращения раз в минуту к базе данных и отправке уведомлений пользователям. Основным потоком запаскается bot.polling для постоянного опроса сервера телеграм ботом для получения новых сообщений.

Файл sqlrequests.py содержит в себе запросы к базе данных. В качестве СУБД используется SQLite. Файл bot.py — бот телеграм, содержит основную логику приложения.

При вводе команды /start в базе данных sqlite3 в таблице users создаётся запись с полями chatid и name, где  chatid — идентификатор чата в телеграм, name — имя пользователя в телеграм. Также  создаётся новая таблица (если её ещё нет) tasks_chatid (tasks_ + id пользователя) с полями: заголовок задачи, описание залачи, тэг, дата создания, дата старта, дата дедлайна, дата начала выполнения, дата завершения, время уведомления, статус и время выполнения задачи. Все даты хранятся в базе типом integer в виде unix time, секундах с начала эпохи (00:00:00 UTC 1 января 1970 года). 

Команды бота:
* /add_task — создаёт новую задачу. Начинает диалог бота с пользователем, в котором пользователь вводит значения полей.
* /cancel — отмена создания задачи. Выход из диалога с ботом.
* /tasks — Список актуальных для пользователя задач (не завершенных и не просроченных). Выводит inline меню с кнопками задач, при нажатии на которые выводится описание задачи и новое inline меню с кнопками выбора действий, применимых в ранее выбранной задаче.
* /all_tasks — выводит список всех задач из БД отдельными сообщениями.
* /overdue_tasks — выводит список всех просроченных задач из БД отдельными сообщениями.
* /completed — выводит список всех завершенных задач из БД отдельными сообщениями.
* /statistic — выводит статистику пользователя. Количество актуальных, выполненных, не выполненных задач и среднее время выполнения задач.

Для запуска проекта в docker контейнере используется docker-compose для возможности автоматического перезапуска контейнера в случае падения приложения, и хранения файла базы данных на отдельном volume. Сам docker-compose.yml не опубликован т. к. в нем содержатся секреты. Для запуска контейнера необходима только одна переменная среды — TELEGRAM_TOKEN. При сборке образа с помощью Dockerfile устанавливаются библиотеки из файла с зависимостями requirements.txt

environment: TELEGRAM_TOKEN


[Ссылка на резюме](https://yoshkar-ola.hh.ru/resume/1f941b4dff07b5c6170039ed1f654842796f52)
