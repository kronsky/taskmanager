FROM python:alpine

WORKDIR /app

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

CMD [ "python", "main.py" ]