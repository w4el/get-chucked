# Get Chucked!! — Cloud Computing Mini-Project (Flask + JWT + Cloud Postgres)

## Introduction

This mini-project applies and extends the techniques practised during the labs to build a prototype cloud application using **Python** and **Flask**.

The project demonstrates:
- A **REST-based service interface** with CRUD operations
- **Integration with an external REST API**
- Use of an **external cloud database** for persistent storage
- **User authentication and access control**
- Clear documentation in code and in this `README.md`

---

## Application Domain

**Get Chucked!!** is a joke management application based on Chuck Norris jokes.

Authenticated users can:
- Fetch jokes from an external public REST API
- Filter jokes by category
- Store jokes in a cloud database
- Perform full CRUD operations on stored jokes (create/read/update/delete)

A simple single-page web UI (React via CDN) is included to demonstrate the features.

---

## Coursework Requirements Mapping

### 1) REST API providing CRUD operations

The application exposes REST endpoints with meaningful status codes and JSON responses.

**Authentication**
- `POST /auth/register` — create a new user account
- `POST /auth/login` — authenticate a user and return a JWT

**Jokes (JWT required)**
- `GET /jokes` — list jokes for the authenticated user
- `GET /jokes/<id>` — retrieve a specific joke
- `POST /jokes` — create a user-submitted joke
- `PUT /jokes/<id>` — update a joke
- `DELETE /jokes/<id>` — delete a joke

---

### 2) Interaction with an external REST service (3 points)

This project integrates with the public **Chuck Norris Jokes API**:
- https://api.chucknorris.io

Endpoints that use the external API (JWT required):
- `GET /categories` — fetch available categories from the external API
- `GET /random` — fetch a random joke from the external API and store it
- `GET /random?category=<name>` — fetch a category-specific joke and store it

Fetched jokes are stored in the database and associated with the authenticated user.

---

### 3) External cloud database persistence

Persistent storage is provided by **Heroku Postgres (managed PostgreSQL)**.

The application connects using a SQLAlchemy database URI stored in:
- `DATABASE_URL` (provided via `.env` or environment variables)

Stored entities include:
- Users (username + **hashed** password)
- Jokes (external jokes saved per user + user-submitted jokes)

---

### 4) Documentation

- Code includes docstrings and human-readable comments where applicable
- This README documents setup, endpoints, and how the project meets the marking criteria

---

## Option 2 Features

This project demonstrates Option 2 items:
- **Serving the application over HTTPS (demo)** using development certificates (`cert.pem` / `key.pem`)
- **Hash-based authentication** (password hashing)
- **User accounts and access management** using JWT-protected endpoints

---

## Technology Stack

- **Backend:** Python, Flask
- **Authentication:** Flask-JWT-Extended (JWT)
- **Database:** PostgreSQL (Heroku Postgres)
- **ORM:** Flask-SQLAlchemy / SQLAlchemy
- **External API:** Chuck Norris API (api.chucknorris.io)
- **UI:** React (CDN) + JSX (Babel) served from `templates/index.html`

---

## Project Structure

```text
cloud_app_with_ui/
├── app.py
├── config.py
├── models.py
├── requirements.txt
├── templates/
│   └── index.html
├── static/
│   └── logo.png
├── cert.pem
└── key.pem

Note: The repository does not include a Python virtual environment (venv/).
A local venv is created during setup (instructions below).


## Setup Instructions (Windows / PowerShell)
```
### 1) Clone the repository and enter the folder

```powershell
git clone https://github.com/w4el/get-chucked
cd cloud_app_with_ui
```

### 2) Create and activate a virtual environment

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
venv\Scripts\Activate.ps1
```

### 3) Install dependencies

```powershell
pip install -r requirements.txt
```

### 4) Configuration (.env included)

A `.env` file has been **included in this repository** for assessment convenience. It contains the necessary database connection string and secrets.

* `DATABASE_URL`: Pre-configured to the cloud Postgres instance.
* `SSL_CERT` / `SSL_KEY`: Pre-configured for the included `cert.pem` and `key.pem`.

No action is required for this step; the application will load these settings automatically.

> `DATABASE_URL` must point to the **Heroku Postgres** instance used by this project.


### 5) Run the application

```powershell
python app.py
```

Open in browser:

* `https://localhost:5000`

> Browsers may show a certificate warning because the HTTPS certificate is for development/demo use.

---

## Using the Web UI

1. Open the home page (`/`)
2. Register a new user
3. Login (UI receives and uses the JWT automatically)
4. Select a category (optional)
5. Fetch a random joke (saved to the database)
6. List stored jokes (scoped to the logged-in user)
7. Add your own joke
8. Update / delete jokes using the UI controls

---

## Quick API Proof (JWT Access Control)

### Without JWT (should fail)

```powershell
Invoke-RestMethod -Method GET -Uri "https://localhost:5000/jokes"
```

Expected: missing/invalid authorization header error.

### With JWT (should succeed)

```powershell
$token = "<PASTE_JWT_HERE>"

Invoke-RestMethod -Method GET -Uri "https://localhost:5000/jokes" -Headers @{
  Authorization = "Bearer $token"
} | ConvertTo-Json -Depth 5
```

---

Thats it Get Chucked!! :)




