FROM python:3

RUN apt-get update && apt-get -y install cron

COPY crontab /etc/cron.d/crontab

RUN chmod 0644 /etc/cron.d/crontab

RUN crontab /etc/cron.d/crontab

RUN ln -sf /usr/share/zoneinfo/Europe/Berlin /etc/localtime

WORKDIR /usr/src/app

COPY app.py ./

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "cron", "-f" ]