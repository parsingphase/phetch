FROM python:3.9-buster

MAINTAINER Richard George <richard@phase.org>

RUN apt-get update
RUN apt install -y pipenv virtualenv python-pyexiv2

VOLUME /root/phetch
VOLUME /mnt/photos

WORKDIR /root/phetch
# RUN virtualenv -p /usr/local/bin/python /root/phetch
ENV SHELL=/bin/bash
RUN pipenv --python 3.9 install

CMD pipenv shell