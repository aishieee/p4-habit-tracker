# Habit Tracker

**Habit Tracker** is a full-stack Django web application designed to help users build better habits by tracking their daily progress and monitering this over time. Developed as part of my Milestone Project 4 for the Code Institute's Full Stack Software Developer course. This project showcases the culmination of all modules covered throughout the programme. 

## Purpose
The purpose of this app is to support users in forming positive habits and maintaining consistency. Users can create and manage their own habits, track their completion using an intuitive calendar, and unlock motivational badges as they progress.


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

