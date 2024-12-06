# wildforge-api

## Running Dev

#### Setup Python Virtual Environment
```bash
$ python3 -m venv venv
$ source venv/bin/activate

# install the requirements
$ pip3 install -r requirements.txt
```

To deactivate virtual environment
```bash
$ deactivate
```

#### Running MySQL DB and PhpMyAdmin
```bash
$ sudo docker-compose up --build -d
```

#### Running MySQL only
```bash
$ cd mysql
$ sudo docker build . -t wildforge-db
$ sudo docker run -d -p 3306:3306 --name wildforge-db -e MYSQL_ROOT_PASSWORD=1234 wildforge-db
```

check if wildforge-db is running 

#### Running Django REST API
```bash
$ python3 backend/manage.py makemigrations && python3 backend/manage.py migrate && python3 backend/manage.py runserver 0.0.0.0:8000
```

#### Running Test
```bash
$ python3 backend/manage.py test
```

### Swagger Endpoint
http://0.0.0.0:8000/swagger/