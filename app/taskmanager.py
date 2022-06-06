import time
import logging
import sqlrequests

logger = logging.getLogger('taskmanager')
handler = logging.FileHandler('logs.txt')
handler.setFormatter(logging.Formatter(fmt='[%(asctime)s: %(levelname)s] %(message)s'))
logger.addHandler(handler)


class Task:
    def __init__(self, chatid, title, description, reminder, start, deadline):
        self.chatid = chatid
        self.title = title
        self.description = description
        self.creation = int(time.time())
        self.reminder = reminder
        self.start = start
        self.deadline = deadline
        self.begin = None
        self.end = None
        self.runtime = None
        self.status = 'created'

    def __str__(self):
        return f'chatid = {self.chatid} title = {self.title}, ' \
               f'description = {self.description}, date of creation = {self.creation}'

    @property
    def chatid(self):
        return self.__chatid

    @chatid.setter
    def chatid(self, chatid):
        if type(chatid) == int:
            self.__chatid = chatid
        else:
            raise ValueError('chatid not integer')

    @property
    def reminder(self):
        return self.__reminder

    @reminder.setter
    def reminder(self, reminder):
        if type(reminder) == int:
            self.__reminder = reminder
        else:
            raise ValueError('reminder not integer')

    @property
    def start(self):
        return self.__start

    @start.setter
    def start(self, start):
        if type(start) == int:
            self.__start = start
        else:
            raise ValueError('start not integer')

    @property
    def deadline(self):
        return self.__deadline

    @deadline.setter
    def deadline(self, deadline):
        if type(deadline) == int:
            self.__deadline = deadline
        else:
            raise ValueError('deadline not integer')

    @staticmethod
    def create_table(chatid):
        sqlrequests.create_user_tasks_table(chatid)

    def write(self, chatid):
        sqlrequests.write_task(self, chatid)

    @staticmethod
    def table_is(chatid):
        if sqlrequests.get_tables_with_chatid(chatid):
            return True
        else:
            return False

    @staticmethod
    def get_tasks(chatid):
        return sqlrequests.get_tasks(chatid)

    @staticmethod
    def get_status(chatid, rowid):
        return sqlrequests.get_status(chatid, rowid)

    @staticmethod
    def begin(chaid, rowid):
        pass

    @staticmethod
    def end(chaid, rowid, end_time):
        pass

    @staticmethod
    def delete(chaid, rowid):
        pass
