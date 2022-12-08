FROM python:3.10-alpine3.16

WORKDIR /app-bet-games

RUN apk update && apk upgrade && \
    apk add --no-cache bash git openssh

RUN apk add --no-cache gcc musl-dev linux-headers

COPY ./requirements.txt /app-bet-games/requirements.txt

RUN pip install -r requirements.txt

COPY . /app-bet-games

ENV PIP_ROOT_USER_ACTION=ignore
ENV FLASK_APP=run.py
ENV FLASK_ENV=development

EXPOSE 9000
CMD ["flask", "--app", "game_app", "run", "--host=0.0.0.0"]
