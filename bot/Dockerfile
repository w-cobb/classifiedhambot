FROM python:3.13

RUN mkdir -p /usr/src/bot
WORKDIR /usr/src/bot

COPY requirements.txt /usr/src/bot

RUN pip3 install -r requirements.txt

COPY . /usr/src/bot

CMD ["python3","-u", "bot.py"]