# Django stock tracker

This is a web application built with python flask. It allows the user to track the overall value of their stock portfolio, which could be useful if it is spread across multiple accounts and wrappers, eliminating the need to log into each separately and manually total them all.


## Dependencies

- Python 3.9.9 (the program should function with any python 3 version)
- Django 4.0
- Requests library https://docs.python-requests.org/
- Yahoo finance API key https://www.yahoofinanceapi.com/

## Setup

To get the program running locally, download the repo files and follow the standard steps for running a Django application.

Beginners to Django should refer to the 'first steps' section of the documentation here: https://docs.djangoproject.com/en/4.0/

Broadly, you need to:

- Install python
- Create a virtual environment (optional but recommended)
- Install Django in your venv
- Install requests library
- Navigate to the project directory in your terminal and run ```python manage.py makemigrations```, ```python manage.py migrate```, then ```python manage.py runserver``` to start the application.

You will also need to change the self.yahoo_api_key attribute of the StockCheck class to reference your own API key, or alternatively create a .env file in the portfolio directory and use environ to avoid hardcoding https://django-environ.readthedocs.io/en/latest/.

## How it works

The app allows the user to track their holdings, hence the bulk of the code in in the holdings directory. Portfolio is the main project directory containing settings.py. The home directory contains styling, including the 'base.html' template, and registration and login templates.

Two models are created in holdings/models.py, Holding and Rate. Each Holding is linked to a user via a one-to-many field.

The app follows a standard CRUD format allowing the user to create, update and delete their holdings and also to add new currencies. Most of the views in holdings/views.py

The app uses the yahoo finance API to update the prices of the holdings and rates. This functionality is all handled by the StockCheck class created in stock_check.py.
