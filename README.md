# Train-Station

API service for Train System management written on DRF

## Installation using GitHub

For beginning you have to install Python3+, PostgresSQL and create db
In terminal write down following command:

```shell
git clone https://github.com/VolodymyrSemchysyn/Train-Station
cd Train-Station
python -m venv venv 
source venv/bin/activate 
pip install -r requirements.txt

python manage.py migrate
python manage.py runserver
```

## Run with docker

Docker should be installed

```shell
docker-compose build
docker-compose up
```

## Getting access

```shell
• create user via /api/user/register/
• get access token via /api/user/token/
```

## Features

```
Trains and Train Types:
This module manages data about trains, including their names, the number of cargo units, seats per cargo, train types, and associated images. Train types are stored in a separate model, which defines classifications for trains.

Crew:
This module stores information about crew members, including their first and last names. Crew members can be assigned to specific journeys.

Tickets and Orders:
The ticketing and order system allows users to create orders containing tickets. Tickets include details about the cargo, seat, and the journey they belong to. Validation is implemented to ensure ticket accuracy and prevent errors.

Stations:
This module contains data about train stations, including their names, latitude, and longitude.

Routes:
Routes define the path between two stations (source and destination) and store information about the distance between them.

Journeys:
The journey management module stores information about routes, trains, departure times, arrival times, and crew members assigned to the journey.
User System: This system facilitates the creation of user profiles, updating user information,
and the differentiation of users based on their permissions or rights.
```

## Database Structure
![db.png](media/uploads/db.png)
## Home page
![img_1.png](media/uploads/img_1.png)