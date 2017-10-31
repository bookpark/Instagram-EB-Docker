FROM        base
MAINTAINER  bkbkgg@gmail.com

ENV         LAN C.UTF-8

COPY        . /srv/app
RUN         /root/.pyenv/versions/app/bin/pip install -r /srv/app/requirements.txt
