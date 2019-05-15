# Example Flask microblog with REST API and unittests

По мотивам этой статьи:  
[правильная структура flask приложения](https://the-bosha.ru/2016/06/03/python-flask-freimvork-pravilnaia-struktura-prilozheniia/).  
Добавленна регистрация и аутентификация, а также API и тесты. В качестве базы данных используется PostgreSQL.  

## Setup

```
python3 -m venv myvenv
source myvenv/bin/activate
pip3 install -r requirements.txt
export APP_SETTINGS="config.DevelopmentConfig"
# DBUSERNAME, DBPASSWORD и DBNAME необходимо заменить на свои реквизиты доступа к БД
export DATABASE_URL='postgresql://DBUSERNAME:DBPASSWORD@localhost/DBNAME'
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
python manage.py runserver
```

### Структура приложения:  
- app/auth/ - регистрация и аутентификация  
- app/main/ - добавление, редактирование, удаление и отображение сообщений  
- app/api/  - REST API  

#### Запуск тестов:  
python3 tests.py  

### Примеры запросов к API:  
- http GET http://127.0.0.1:5000/api/posts  
- http GET http://127.0.0.1:5000/api/posts/2  
- Полноценная реализация POST, PUT, DELETE планируется после того как будет сделана аутентификацию к API.  
- http POST http://127.0.0.1:5000/api/posts name="Post name" content="Post content"  
- http PUT http://127.0.0.1:5000/api/posts/2 content="Text post" name="Name post"  
- http DELETE http://127.0.0.1:5000/api/posts/2  






