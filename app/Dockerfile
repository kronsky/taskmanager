FROM python:alpine

WORKDIR /app

RUN pip install --upgrade pip

RUN pip install pyTelegramBotAPI

COPY . .

CMD [ "python", "main.py" ]