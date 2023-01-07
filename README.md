# Sport Game Bet
> The application for bet sport games in chosen tournament.

## Table of Contents
* [General Info](#general-information)
* [Technologies Used](#technologies-used)
* [Features](#features)
* [Setup](#setup)
* [Usage](#usage)
* [Project Status](#project-status)
* [Room for Improvement](#room-for-improvement)


## General Information
- This project was created because I wanted to try to implement Flask functions for create simple web app.
- I wanted to learn more about the mysql database. 


## Technologies Used
- Python - version 3.10.6
- Flask - version 2.2.2
- mysql - version 8.0.31


## Features
List the ready features here:
- database for user, tournament, game and bet results
- register and login user
- admin page 
- user bet page for show results
- create user group for create team table
- implementation for load json file
- implementation for load photos and save it in database
- implementation in docker


## Setup
For start application with docker you need [Docker](https://docs.docker.com/get-docker/) and [docker-compose](https://docs.docker.com/compose/install/).


## Usage
The application can be build from sources or can be run in docker.


##### Build from sources
```bash
$ # Move to directory
$ cd folder/to/clone-into/
$
$ # Clone the sources
$ git clone https://github.com/mateuszgua/game_typer.git
$
$ # Move into folder
$ cd game_type_app
$
$ # Create virtual environment
$ python3 -m venv my_env
$
$ # Activate the virtual environment
$ source my_env/bin/activate
$
$ # Start app
$ flask --app run.py run
$ # ...
$ # * Running on http://127.0.0.1:5000  
```

##### Start the app in Docker
```bash
$ # Move to directory
$ cd folder/to/clone-into/
$
$ # Clone the sources
$ git clone https://github.com/mateuszgua/game_typer.git
$
$ # Move into folder
$ cd game_type_app
$
$ # Start app
$ docker-compose up --build
$ # ...
$ # backend_1  |  * Running on http://127.0.0.1:5000
```


## Project Status
Project is: _in progress_ 


## Room for Improvement
Include areas you believe need improvement / could be improved. Also add TODOs for future development.

Room for improvement:
- Improve the addition of tournaments

To do:
- Create demo in nginx
