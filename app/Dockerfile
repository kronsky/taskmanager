FROM python:alpine

WORKDIR /app

COPY . .

RUN pip install --upgrade pip && pip install -r requirements.txt

RUN mkdir databasev

CMD [ "python", "main.py" ]