FROM python:3.10-alpine3.16

WORKDIR /game_app

#
RUN pip install --upgrade pip

RUN apk update && apk upgrade && \
    apk add --no-cache bash git openssh

#
RUN apk add --no-cache gcc musl-dev linux-headers

COPY ./requirements.txt /game_app/requirements.txt

#RUN pip install -r requirements.txt

COPY . /game_app

#
ENV VIRTUAL_ENV=/home/mateusz/Learn/game_type_app/my_env
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

ENV PIP_ROOT_USER_ACTION=ignore
# ENV FLASK_APP=run.py
RUN export FLASK_APP=app.py
RUN pip install -r requirements.txt

EXPOSE 5000
CMD ["flask", "--app", "game_app", "run", "--host=0.0.0.0"]
# CMD ["flask", "run", "--host=0.0.0.0"]
# CMD ["flask", "run", "--host", "0.0.0.0"]
# CMD python run.py
# CMD ["python", "run.py"]
