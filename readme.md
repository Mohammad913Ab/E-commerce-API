# Django Store API

A RESTful API built with Django & Django REST Framework for a simple store.

## Features
- [x] User registration/login (basic DRF auth)
- [ ] Product management (CRUD)
- [ ] Order system (Coming soon)
- [ ] Admin control
- [ ] API documentation

## Stack
- Python 3
- Django 4
- Django REST Framework
- SQLite3 (Dev DB)

## Setup

```bash
git clone https://github.com/Mohammad913Ab/E-commerce-API
cd E-commerce-API
python -m venv .venv
source .venv/bin/activate  # on Linux/macOS
# or .venv\Scripts\activate  # on Windows
pip install -r requirements.txt
python manage.py runserver
