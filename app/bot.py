import telebot
from config import telegram_token
from telebot import types, custom_filters
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage
from datetime import datetime, timedelta
from taskmanager import Table, Task
import time

state_storage = StateMemoryStorage()
bot = telebot.TeleBot(telegram_token, state_storage=state_storage)


class BotStates(StatesGroup):
    title = State()
    description = State()
    reminder = State()
    start_date = State()
    start_time = State()
    deadline_date = State()
    deadline_time = State()


def convert_time_from_timestamp(timestamp):
    if type(timestamp) == int:
        return time.strftime('%Y-%m-%d %H:%M', time.gmtime(timestamp))
    elif timestamp is None:
        return timestamp


def date_button():
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    aftertomorrow = today + timedelta(days=2)
    menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    b1 = types.KeyboardButton(str(today))
    b2 = types.KeyboardButton(str(tomorrow))
    b3 = types.KeyboardButton(str(aftertomorrow))
    menu.add(b1, b2, b3)
    return menu


def time_button():
    menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    b1, b2, b3, b4, b5, b6, b7, b8, b9, b10, b11, b12, b13, b14, b15, b16, b17 =\
        [types.KeyboardButton(f'{i:02}:00') for i in range(7, 24)]
    b18, b19, b20, b21, b22, b23, b24 = \
        [types.KeyboardButton(f'{i:02}:00') for i in range(0, 7)]
    menu.add(b1, b2, b3, b4, b5, b6, b7, b8, b9, b10, b11, b12, b13, b14,
             b15, b16, b17, b18, b19, b20, b21, b22, b23, b24)
    return menu


def message_about_no_table(chatid):
    bot.send_message(chatid, 'Вы по какой-то причине отсутсвуете в базе данных,'
                             ' введите команду /start')


@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name
    bot.send_message(message.chat.id, text='Привет, ' + name +
                                           '!\nСписок команд:\n'
                                           '/add_task - создать новую задачу\n'
                                           '/cancel - отмена создания задачи\n'
                                           '/tasks - актуальные задачи\n'
                                           '/all_tasks - все задачи\n'
                                           '/overdue_tasks - просроченные задачи\n'
                                           '/completed - уже выполненные задачи\n'
                                           '/statistic - статистика')
    Table.create_table(message.chat.id)


@bot.message_handler(commands=['add_task'])
def add_task(message):
    if not Table.table_is(message.chat.id):
        message_about_no_table(message.chat.id)
    else:
        bot.set_state(message.from_user.id, BotStates.title, message.chat.id)
        bot.send_message(message.chat.id, 'Введите заголовок задачи')


@bot.message_handler(state="*", commands=['cancel'])
def any_state(message):
    bot.send_message(message.chat.id, "Отмена создания задачи",
                     reply_markup=types.ReplyKeyboardRemove())
    bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(state=BotStates.title)
def get_title(message):
    bot.send_message(message.chat.id, 'Введите описание задачи')
    bot.set_state(message.from_user.id, BotStates.description, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['title'] = message.text


@bot.message_handler(state=BotStates.description)
def get_description(message):
    menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    b1 = types.KeyboardButton('5')
    b2 = types.KeyboardButton('10')
    b3 = types.KeyboardButton('15')
    b4 = types.KeyboardButton('20')
    b5 = types.KeyboardButton('30')
    b6 = types.KeyboardButton('60')
    menu.add(b1, b2, b3, b4, b5, b6)
    bot.send_message(message.chat.id, 'За сколько минут напомнить?', reply_markup=menu)
    bot.set_state(message.from_user.id, BotStates.reminder, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['description'] = message.text


@bot.message_handler(state=BotStates.reminder, is_digit=True)
def get_reminder(message):
    menu = date_button()
    bot.send_message(message.chat.id, 'Введите дату начала задачи в формате гггг-мм-дд или',
                     reply_markup=menu)
    bot.set_state(message.from_user.id, BotStates.start_date, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['reminder'] = message.text


@bot.message_handler(state=BotStates.start_date, is_date=True)
def get_start_date(message):
    menu = time_button()
    bot.send_message(message.chat.id, 'Введите время начала задачи в формате чч:мм',
                     reply_markup=menu)
    bot.set_state(message.from_user.id, BotStates.start_time, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['start_date'] = message.text


@bot.message_handler(state=BotStates.start_time, is_time=True)
def get_start_time(message):
    menu = date_button()
    bot.send_message(message.chat.id, 'Введите дату крайнего срока в формате гггг-мм-дд',
                     reply_markup=menu)
    bot.set_state(message.from_user.id, BotStates.deadline_date, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['start_time'] = data['start_date'] + ' ' + message.text
        data['start_time'] = datetime.strptime(data['start_time'], '%Y-%m-%d %H:%M')


@bot.message_handler(state=BotStates.deadline_date, is_date=True)
def get_deadline_date(message):
    menu = time_button()
    bot.send_message(message.chat.id, 'Введите время крайнего срока в формате чч:мм',
                     reply_markup=menu)
    bot.set_state(message.from_user.id, BotStates.deadline_time, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['deadline_date'] = message.text


@bot.message_handler(state=BotStates.deadline_time, is_time=True)
def get_deadline_time(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['deadline_time'] = data['deadline_date'] + ' ' + message.text
        data['deadline_time'] = datetime.strptime(data['deadline_time'], '%Y-%m-%d %H:%M')
        task = (f"Создана задача: \n"
                f"=> Задача: {data['title']} \n"
                f"=> Описание: {data['description']} \n"
                f"=> Напомнить за (минут): {data['reminder']} \n"
                f"=> Дата и время старта: {data['start_time']} \n"
                f"=> Дата и время конца срока: {data['deadline_time']}")
        bot.send_message(message.chat.id, task, reply_markup=types.ReplyKeyboardRemove())
    task = Task(message.chat.id, data['title'], data['description'], int(data['reminder']) * 60,
                int(data['start_time'].timestamp()), int(data['deadline_time'].timestamp()))
    task.write(message.chat.id)
    bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(commands=['tasks'])
def get_tasks(message):
    if not Table.table_is(message.chat.id):
        message_about_no_table(message.chat.id)
    else:
        tasks = Task.get_tasks(message.chat.id)
        markup = telebot.types.InlineKeyboardMarkup()
        for task in tasks:
            callback = 'get:' + str(task[0])
            markup.add(telebot.types.InlineKeyboardButton(text=task[1], callback_data=callback))
        if len(tasks) != 0:
            bot.send_message(message.chat.id, text="Выберите задачу:", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, 'Задач нет')


def tasks_message(message, tasks):
    for task in tasks:
        if task[9]:
            runtime = timedelta(seconds=task[9])
        else:
            runtime = 'None'
        bot.send_message(message.chat.id,
                         f"<b>{task[1]}\n{task[2]}</b>\n"
                         f"Дата создания: <b>{convert_time_from_timestamp(task[3])}</b> \n"
                         f"Дата начала выполнения: <b>{convert_time_from_timestamp(task[7])}</b> \n"
                         f"Дата выполнения: <b>{convert_time_from_timestamp(task[8])}</b> \n"
                         f"Время выполнения: <b>{runtime}</b>\n"
                         f"Статус: <b>{task[10]}</b>", parse_mode='html')


@bot.message_handler(commands=['all_tasks'])
def get_tasks(message):
    if not Table.table_is(message.chat.id):
        message_about_no_table(message.chat.id)
    else:
        tasks = Task.get_all_tasks(message.chat.id)
        if len(tasks) != 0:
            tasks_message(message, tasks)
        else:
            bot.send_message(message.chat.id, 'Задач нет')


@bot.message_handler(commands=['overdue_tasks'])
def get_overdue_tasks(message):
    if not Table.table_is(message.chat.id):
        message_about_no_table(message.chat.id)
    else:
        tasks = Task.get_overdue_task(message.chat.id)
        if len(tasks) != 0:
            tasks_message(message, tasks)
        else:
            bot.send_message(message.chat.id, 'Задач нет')


@bot.message_handler(commands=['completed'])
def get_completed_tasks(message):
    if not Table.table_is(message.chat.id):
        message_about_no_table(message.chat.id)
    else:
        tasks = Task.get_completed_tasks(message.chat.id)
        if len(tasks) != 0:
            tasks_message(message, tasks)
        else:
            bot.send_message(message.chat.id, 'Задач нет')


@bot.message_handler(commands=['statistic'])
def get_statistic(message):
    if not Table.table_is(message.chat.id):
        message_about_no_table(message.chat.id)
    else:
        runtimes = Task.get_runtime(message.chat.id)
        if len(runtimes) != 0:
            timeslist = []
            for runtime in runtimes:
                if type(runtime[0]) is int:
                    timeslist.append(runtime[0])
            try:
                runtime = timedelta(seconds=int(sum(timeslist) / len(timeslist)))
            except ZeroDivisionError:
                runtime = None
            bot.send_message(message.chat.id, f'Статистика пользователя {message.from_user.first_name}:\n'
                                              f'=> количество активных задач: '
                                              f'{len(Task.get_tasks(message.chat.id))}\n'
                                              f'=> количество выполненных задач: '
                                              f'{len(Task.get_completed_tasks(message.chat.id))}\n'
                                              f'=> количество просроченных задач: '
                                              f'{len(Task.get_overdue_task(message.chat.id))}\n'
                                              f'=> среднее время выполнения: {runtime}')
        else:
            bot.send_message(message.chat.id, 'У вас пока небыло ни одной задачи')


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    tasks = Task.get_tasks(call.message.chat.id)
    if call.data[:3] == 'get':
        for task in tasks:
            if str(task[0]) == call.data[4:]:
                markup = telebot.types.InlineKeyboardMarkup()
                markup.add(telebot.types.InlineKeyboardButton
                           ('Начать выполнение', callback_data='bgn:' + str(task[0])))
                markup.add(telebot.types.InlineKeyboardButton
                           ('Завершить задачу', callback_data='end:' + str(task[0])))
                markup.add(telebot.types.InlineKeyboardButton
                           ('Удалить задачу', callback_data='del:' + str(task[0])))
                bot.send_message(call.message.chat.id,
                                 f"Задача: {task[1]} \n"
                                 f"Описание: {task[2]} \n"
                                 f"Дата создания: {convert_time_from_timestamp(task[3])} \n"
                                 f"Напоминание: за {int(task[4] / 60)} минут \n"
                                 f"Дата начала: {convert_time_from_timestamp(task[5])} \n"
                                 f"Крайник срок: {convert_time_from_timestamp(task[6])} \n"
                                 f"Дата начала выполнения: {convert_time_from_timestamp(task[7])} \n"
                                 f"Дата выполнения: {convert_time_from_timestamp(task[8])} \n"
                                 f"Статус: {task[10]}", reply_markup=markup)
    elif call.data[:3] == 'bgn':
        if Task.get_status(call.message.chat.id, call.data[4:]) != 'begined':
            Task.begin(call.message.chat.id, call.data[4:])
            bot.send_message(call.message.chat.id, 'Начато выполнение задачи')
        else:
            bot.send_message(call.message.chat.id, 'Выполнение задачи уже было начато ранее!')
    elif call.data[:3] == 'end':
        if Task.get_status(call.message.chat.id, call.data[4:]) == 'begined':
            Task.end(call.message.chat.id, call.data[4:])
            bot.send_message(call.message.chat.id, 'Задача выполнена')
        elif Task.get_status(call.message.chat.id, call.data[4:]) == 'created':
            Task.end(call.message.chat.id, call.data[4:])
            bot.send_message(call.message.chat.id, 'Задача была начала и сразу выполнена')
    elif call.data[:3] == 'del':
        Task.delete(call.message.chat.id, call.data[4:])
        bot.send_message(call.message.chat.id, 'Задача удалена')
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)


@bot.message_handler(state=BotStates.reminder, is_digit=False)
def reminder_incorrect(message):
    bot.send_message(message.chat.id, 'Вы ввели не число, попробуйте еще раз')


@bot.message_handler(state=BotStates.start_date, is_date=False)
def start_date_incorrect(message):
    bot.send_message(message.chat.id, 'Неверный формат даты, введите дату в формате гггг-мм-дд '
                                      'или нажмите на кнопку')


@bot.message_handler(state=BotStates.deadline_date, is_date=False)
def deadline_date_incorrect(message):
    bot.send_message(message.chat.id, 'Неверный формат даты, введите дату в формате гггг-мм-дд '
                                      'или нажмите на кнопку')


@bot.message_handler(state=BotStates.start_time, is_date=False)
def start_time_incorrect(message):
    bot.send_message(message.chat.id, 'Неверный формат времени, введите время в формате чч:мм '
                                      'или нажмите на кнопку')


@bot.message_handler(state=BotStates.deadline_time, is_date=False)
def deadline_time_incorrect(message):
    bot.send_message(message.chat.id, 'Неверный формат времени, введите время в формате чч:мм '
                                      'или нажмите на кнопку')


class IsDate(telebot.custom_filters.SimpleCustomFilter):
    key = 'is_date'

    def check(self, message):
        try:
            datetime.strptime(message.text, '%Y-%m-%d')
            return True
        except ValueError:
            return False


class IsTime(telebot.custom_filters.SimpleCustomFilter):
    key = 'is_time'

    def check(self, message):
        try:
            datetime.strptime(message.text, '%H:%M')
            return True
        except ValueError:
            return False


bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(custom_filters.IsDigitFilter())
bot.add_custom_filter(IsDate())
bot.add_custom_filter(IsTime())
