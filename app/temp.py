from taskmanager import Task

t1 = Task(12345678, 'Тестовая задача', 'Описание тестовой задачи', 10, 1654516286, 1654516286)

print(t1)

t1.create_table(12345678)
t1.write(12345678)
