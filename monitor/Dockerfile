FROM python:3.13

RUN mkdir -p /usr/src/monitor
WORKDIR /usr/src/monitor

COPY requirements.txt /usr/src/monitor

RUN pip3 install -r requirements.txt

COPY . /usr/src/monitor

CMD ["python3","-u", "monitor.py"]