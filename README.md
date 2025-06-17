# Habit Tracker

**Habit Tracker** is a full-stack Django web application designed to help users build better habits by tracking their daily progress and monitering this over time. Developed as part of my Milestone Project 4 for the Code Institute's Full Stack Software Developer course. This project showcases the culmination of all modules covered throughout the programme. 

## Purpose
The purpose of this app is to support users in forming positive habits and maintaining consistency. Users can create and manage their own habits, track their completion using an intuitive calendar, and unlock motivational badges as they progress.

## Features
This Habit Tracker project was developed using **Django 4** in conjunction with **Bootstrap 5**, making it a fully responsive and mobile-first app. The application was built as part of **Project 4 (Full Stack Frameworks with Django)**. It draws on all prior modules and integrates both frontend and backend technologies into a single, functioning web app.

Python 3.13.1 was used as the base language, and the project was managed in **Visual Studio Code** with Git and GitHub for version control. The project uses Django’s built-in templating system, URL routing, authentication tools, and Object-Relational Mapping to manage data through a SQLite3 database.

The frontend was built using HTML5, CSS3, JavaScript, and Bootstrap 5, while dynamic user interactions and progress visuals were implemented with JavaScript and Google Charts.

The project boasts a wide range of features:

### Success Messages

The app uses Django’s built-in messages framework to show feedback to users when actions are completed successfully. These messages include:

- ✅ Habit added successfully!
- Habit deleted successfully!


Messages are styled with Bootstrap alert classes and appear at the top of the screen. They fade out automatically after a few seconds using JavaScript, so users don't need to click to dismiss them.

---

### Reminder Emails

The app includes a custom reminder system that checks for incomplete habits and sends reminder emails to users. 

- 🕓 Emails are triggered manually using:
  ```bash
  python3 manage.py send_reminders


## Deployment

This Habit Tracker full-stack web application was developed using **Visual Studio Code** and version controlled with **Git** (locally) and **GitHub** (remotely). Deployment was carried out using **Heroku**, with production settings managed via environment variables and the Config Vars feature provided by the Heroku dashboard.

### Environment Variables

To keep sensitive information safe, secret keys and configuration values were stored in an `env.py` file locally, which was added to the `.gitignore` file to ensure it was not committed to the public repository.

These values were then manually entered into **Heroku** under:

<details>
<summary> Click to view detailed Heroku deployment steps (with commands & screenshots)</summary>

<br>

###  Steps to Deploy on Heroku

#### 1. Project Setup

- Installed **Gunicorn** for WSGI support and updated requirements:
    ```bash
    pip3 install gunicorn
    pip3 freeze > requirements.txt
    ```

- Created a `Procfile` at the project root (no file extension, case-sensitive):
    ```
    web: gunicorn p4_habit_tracker.wsgi
    ```

- Added and committed it:
    ```bash
    git add Procfile
    git commit -m "Add Procfile for Heroku deployment"
    ```

- Installed **Whitenoise** to serve static files:
    ```bash
    pip3 install whitenoise
    pip3 freeze > requirements.txt
    ```

- Updated `settings.py` middleware:
    ```python
    MIDDLEWARE = [
        "django.middleware.security.SecurityMiddleware",
        "whitenoise.middleware.WhiteNoiseMiddleware",  # 👈 Add this line just below SecurityMiddleware
        ...
    ]
    ```

- Updated `STATIC_ROOT` in `settings.py`:
    ```python
    STATIC_ROOT = BASE_DIR / "staticfiles"
    ```

#### 2. Preparing for Deployment

- Ran collectstatic locally to make sure static files are ready:
    ```bash
    python3 manage.py collectstatic --noinput
    ```

- Confirmed files appeared in `/staticfiles/` and ensured only one copy of `styles.css` and `script.js` was in the correct folder.

#### 3. Pushing to Heroku

- Logged into Heroku CLI:
    ```bash
    heroku login
    ```

- Created a new Heroku app:
    ```bash
    heroku create p4-habit-tracker
    ```

- Added the Heroku remote (if needed):
    ```bash
    heroku git:remote -a p4-habit-tracker
    ```

- Deployed the app:
    ```bash
    git push heroku main
    ```

#### 4. Config Vars and Environment Settings

- In the Heroku dashboard:
  - Navigated to **Settings > Config Vars**
  - Added the following:
    ```
    SECRET_KEY: your-django-secret-key
    DEBUG: False
    ```

#### 5. Final Setup Commands

- Ran migrations and created a superuser:
    ```bash
    heroku run python3 manage.py migrate
    heroku run python3 manage.py createsuperuser
    ```

- Optionally removed this (added earlier during testing):
    ```bash
    heroku config:unset DISABLE_COLLECTSTATIC
    ```

- If static files weren't showing up earlier:
    ```bash
    heroku run python3 manage.py collectstatic --noinput
    ```

- Scaled dynos (if required):
    ```bash
    heroku ps:scale web=1
    ```

---

✅ **Live Site**: [https://p4-habit-tracker-535b0b8611ff.herokuapp.com/](https://p4-habit-tracker-535b0b8611ff.herokuapp.com/)

</details>

