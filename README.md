# Get Chucked

A cloud-backed joke manager built with Flask. Users register and log in to get a JSON Web Token, pull jokes from the public [Chuck Norris API](https://api.chucknorris.io), filter them by category, and store and manage their own collection in a PostgreSQL database. A single-page React front end sits on top of the API, and the app can be served over HTTPS.

## Features

- **Accounts:** register and log in; passwords are stored as salted hashes, never in plain text.
- **Token auth:** login returns a JWT, and every data endpoint rejects requests without a valid one.
- **External API integration:** fetch joke categories, or a random joke (optionally from one category), from the Chuck Norris API.
- **Persistence:** fetched jokes are saved to the user's collection without duplicates.
- **Full CRUD:** list, view, add, edit and delete jokes, each scoped to the logged-in user.
- **Web UI:** a React single-page interface (loaded from a CDN, no build step) that handles login and drives every endpoint.
- **HTTPS:** served over TLS when certificates are provided.

## Architecture

```
 React SPA (index.html) ──HTTPS + Bearer JWT──▶ Flask app ──SQLAlchemy──▶ PostgreSQL
                                                    │
                                                    └──requests──▶ api.chucknorris.io
```

The app uses Flask's application factory pattern (`create_app()`), so configuration can be swapped, for example SQLite locally and managed Postgres in the cloud. Settings and secrets come from environment variables loaded from a `.env` file.

### Data model

| Table | Columns | Notes |
|---|---|---|
| `users` | id, username (unique), password_hash | Passwords hashed with Werkzeug |
| `jokes` | id, joke_id, value, category, created_at, user_id | `joke_id` is the external API's ID, null for user-written jokes |

A unique constraint on `(joke_id, user_id)` stops the same external joke being saved twice for one user, while still letting different users save the same joke.

## API

| Method | Path | Auth | Purpose |
|---|---|---|---|
| POST | `/auth/register` | none | Create an account (`201`, or `400` if the username exists) |
| POST | `/auth/login` | none | Check credentials and return a JWT (`200`, or `401`) |
| GET | `/jokes` | JWT | List the user's jokes |
| GET | `/jokes/<id>` | JWT | One joke, only if the user owns it |
| POST | `/jokes` | JWT | Add a user-written joke |
| PUT | `/jokes/<id>` | JWT | Edit a joke the user owns |
| DELETE | `/jokes/<id>` | JWT | Delete a joke the user owns |
| GET | `/categories` | JWT | Categories from the external API |
| GET | `/random?category=` | JWT | Random joke from the external API, saved to the collection |

Errors use meaningful status codes: `400` for missing fields, `401` for missing or invalid credentials, `403` for another user's joke, `404` for not found, and `502` when the external API fails or times out (after 5 seconds).

## Setup (Windows PowerShell)

Requires Python 3.

```powershell
git clone https://github.com/w4el/get-chucked
cd get-chucked
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first.

### Configuration

Copy the example settings and edit them:

```powershell
Copy-Item .env.example .env
```

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | `sqlite:///app.db` for local use, or a Postgres connection string for a cloud database |
| `SECRET_KEY`, `JWT_SECRET_KEY` | Long random strings used to sign sessions and tokens |
| `SSL_CERT`, `SSL_KEY` | Optional paths to TLS certificates for HTTPS |

### Create the database tables

```powershell
flask --app app init-db
```

### HTTPS (optional)

Certificates are not included in the repository. To serve over HTTPS locally, generate your own with [mkcert](https://github.com/FiloSottile/mkcert):

```powershell
mkcert -install
mkcert -cert-file cert.pem -key-file key.pem localhost
```

The app picks up `cert.pem` and `key.pem` from the project folder automatically. Without them it runs over plain HTTP.

### Run

```powershell
python app.py
```

Open `https://localhost:5000` (or `http://localhost:5000` without certificates).

## Using the web UI

1. Register a new user, then log in (the UI stores and sends the JWT for you).
2. Optionally pick a category and fetch a random joke; it is saved to your collection.
3. List your saved jokes, add your own, and edit or delete them.

## Testing access control from the command line

Without a token the request is rejected:

```powershell
Invoke-RestMethod -Method GET -Uri "https://localhost:5000/jokes"
```

With a token from `/auth/login`, replacing `YOUR_TOKEN` with the `access_token` value it returned:

```powershell
$token = "YOUR_TOKEN"
Invoke-RestMethod -Method GET -Uri "https://localhost:5000/jokes" -Headers @{ Authorization = "Bearer $token" } | ConvertTo-Json -Depth 5
```

## Project structure

```text
├── app.py            Flask app factory, routes and external API calls
├── config.py         Configuration and HTTPS certificate lookup
├── models.py         SQLAlchemy models (User, Joke)
├── requirements.txt
├── .env.example      Template for local settings
├── templates/
│   └── index.html    React single-page UI
└── static/
    └── logo.png
```

## Tech stack

Python, Flask, Flask-SQLAlchemy, Flask-JWT-Extended, Werkzeug, PostgreSQL, SQLite, requests, python-dotenv, React (CDN) with Babel.
