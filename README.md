# Vending Management - Minimal Django Scaffold

This is a **minimal** scaffold for the vending management web application requested.
It contains:
- Django project (`vending_project`) compatible with Django 4.2
- App `core` with models for VendingMachine, Product, Sale, ServiceRecord, FranchiseUser
- Templates and static assets with a responsive layout and a JS CAPTCHA implementation
- A simple REST API endpoint for listing vending machines (DRF skeleton)
- Instructions to run locally (see below)

**Notes**:
- This scaffold is meant as a starting point. It does NOT include production settings, email sending, or HTTPS configuration.
- To run: create virtualenv, `pip install -r requirements.txt`, then `python manage.py migrate` and `python manage.py runserver`

