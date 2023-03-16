# Проект «Yatube»

### Описание
Сервис для публикации блогов.

Регистрация пользователей через электронную почту.  
Зарегистрированные пользователи могут создавать посты, оставлять комментарии к постам другим пользователей.  
Не зарегистрированные пользователи могут просматривать посты.  
Реализована система подписок пользователей друг на друга. 

### Технологии:
![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=green)

### Используемые пакеты:
    *  asgiref==3.5.2
    *  atomicwrites==1.4.1
    *  attrs==22.1.0
    *  Django==2.2.16
    *  mixer==7.1.2
    *  Pillow==8.3.1
    *  pytest==6.2.4
    *  pytest-django==4.4.0
    *  pytest-pythonpath==0.7.3
    *  requests==2.26.0
    *  six==1.16.0
    *  sorl-thumbnail==12.7.0
    *  Faker==12.0.1
### Установка

1. Клонировать репозиторий:

   ```python
   git clone ...
   ```

2. Перейти в папку с проектом:

   ```python
   cd yatube/
   ```

3. Установить виртуальное окружение для проекта:

   ```python
   python -m venv venv
   ```

4. Активировать виртуальное окружение для проекта:

   ```python
   # для OS Lunix и MacOS
   source venv/bin/activate
   # для OS Windows
   source venv/Scripts/activate
   ```

5. Установить зависимости:

   ```python
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

6. Выполнить миграции на уровне проекта:

   ```python
   cd yatube
   python3 manage.py makemigrations
   python3 manage.py migrate
   ```

7. Запустить проект:
   ```python
   python manage.py runserver
   ```


### Автор проекта 
* Роман Дячук   
