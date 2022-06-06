from taskmanager import Task

t1 = Task(123456, 'Тестовая задача', 'Описание тестовой задачи', 10, 1654516286, 1654516286)

print(t1)

t1.create_table(123456)
t1.write(123456)
