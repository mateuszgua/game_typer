FROM python:3.10-alpine3.16

WORKDIR /app

RUN apk update && apk upgrade && \
    apk add --no-cache bash git openssh

RUN apk add --no-cache gcc musl-dev linux-headers

COPY ./requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

COPY . /app

ENV PIP_ROOT_USER_ACTION=ignore
ENV FLASK_APP=run.py

EXPOSE 5000
# CMD ["flask", "--app", "game_app", "run", "--host=0.0.0.0"]
# CMD ["flask", "run", "--host=0.0.0.0"]
# CMD ["flask", "run", "--host", "0.0.0.0"]
CMD python run.py
