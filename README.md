# Notice Board

Simple notice board app created with Flask and SQLAlchemy. You can create user, log in, add posts and send messages to other users..

## Getting Started

1) Clone the project:
```
git clone https://github.com/agataldz/notice_board.git
```
2) Create virtual environment:
```
virtualenv venv
```
```
source venv/bin/activate
```
3) Install requirements:
```
pip install -r requirements.txt
```

4) Create a postgres database and add the credentials to app.py
```
postgresql://your_username:your_password@localhost/your_db_name
```
5) Run migrations
```
flask db init
flask db migrate
flask db upgrade
```
