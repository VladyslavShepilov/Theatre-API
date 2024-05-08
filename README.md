# Theatre-API
> API for theatre which can manage all related stuff as superuser
> and make online reservations as a user.

Django, rest-framework, Python 3.11

## Credentials
You can create your own superuser
*  by running
```
python manage.py createsuperuser
```
* for Docker 
```
docker exec -it <container name/id> sh 
python manage.py createsuperuser
```
## Installing / Getting started

Run the code below at shell console

```shell
git clone ...
cd task-manager
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
or use Docker,
```
cp env.sample .env
docker-compose build
docker-compose up
```
Installs requirements and runs django server.

## Features

* JWT authentication
* Admin panel
* Managing tasks through website interface
* Limited access for non-staff users
* Creating tickets to performances
* Uploading images for different plays


## Demo
![Website Interface](demo.png)
