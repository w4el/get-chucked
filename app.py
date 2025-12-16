import os
import requests
from flask import Flask, abort, jsonify, render_template, request
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required

from config import Config, get_ssl_context
from models import Joke, User, db

# Base URL for the external API
CHUCK_API_BASE = "https://api.chucknorris.io/jokes"


def create_app(config_class=Config):
    """
    Flask application factory.
    Initializes the app, database, and JWT manager.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    JWTManager(app)

    # ---- Helper Functions ----

    def json_body():
        """Helper to safely get JSON data from request."""
        return request.get_json(silent=True) or {}

    def require_fields(data, *fields):
        """Helper to validate that required fields exist in the request body."""
        missing = [f for f in fields if not data.get(f)]
        if missing:
            return False, (jsonify({"error": f"missing field(s): {', '.join(missing)}"}), 400)
        return True, None

    def current_user():
        """Helper to get the current authenticated user object."""
        identity = get_jwt_identity()
        try:
            user_id = int(identity)
        except (TypeError, ValueError):
            abort(401)

        user = db.session.get(User, user_id)
        if user is None:
            abort(401)
        return user

    # ---- CLI Commands ----

    @app.cli.command("init-db")
    def init_db():
        """Command to create database tables."""
        with app.app_context():
            db.create_all()
            print("Database tables created successfully.")

    # ---- Authentication Routes ----

    @app.post("/auth/register")
    def register():
        data = json_body()
        ok, resp = require_fields(data, "username", "password")
        if not ok:
            return resp

        username = data["username"]
        password = data["password"]

        if User.query.filter_by(username=username).first():
            return jsonify({"error": "username already exists"}), 400

        # Create new user with hashed password
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return jsonify({"message": f"user {username} created"}), 201

    @app.post("/auth/login")
    def login():
        data = json_body()
        ok, resp = require_fields(data, "username", "password")
        if not ok:
            return resp

        username = data["username"]
        password = data["password"]

        user = User.query.filter_by(username=username).first()
        
        # Check password hash
        if user is None or not user.check_password(password):
            return jsonify({"error": "invalid credentials"}), 401

        # Identity must be a string for JWT
        token = create_access_token(identity=str(user.id))
        return jsonify({"access_token": token}), 200

    # ---- UI Routes ----

    @app.get("/")
    def frontend():
        """Serve the main page."""
        return render_template("index.html"), 200

    # ---- Joke CRUD Operations ----

    @app.get("/jokes")
    @jwt_required()
    def list_jokes():
        user = current_user()
        jokes = Joke.query.filter_by(user_id=user.id).all()
        return jsonify({"jokes": [j.to_dict() for j in jokes]}), 200

    @app.get("/jokes/<int:joke_id>")
    @jwt_required()
    def get_joke(joke_id):
        user = current_user()
        joke = db.session.get(Joke, joke_id)
        
        # Ensure user owns the joke
        if not joke or joke.user_id != user.id:
            return jsonify({"error": "joke not found"}), 404
        return jsonify(joke.to_dict()), 200
    
    @app.post("/jokes")
    @jwt_required()
    def create_joke():
        data = json_body()
        ok, resp = require_fields(data, "value")
        if not ok:
            return resp

        user = current_user()
        # Custom jokes don't have an external ID or category by default
        joke = Joke(joke_id=None, value=data["value"], category=None, user_id=user.id)
        db.session.add(joke)
        db.session.commit()
        return jsonify(joke.to_dict()), 201

    @app.put("/jokes/<int:joke_id>")
    @jwt_required()
    def update_joke(joke_id):
        joke = Joke.query.get(joke_id)
        if not joke:
            return jsonify({"error": "joke not found"}), 404

        user = current_user()
        if joke.user_id is not None and joke.user_id != user.id:
            return jsonify({"error": "not authorised"}), 403

        data = json_body()
        ok, resp = require_fields(data, "value")
        if not ok:
            return resp

        joke.value = data["value"]
        db.session.commit()
        return jsonify(joke.to_dict()), 200

    @app.delete("/jokes/<int:joke_id>")
    @jwt_required()
    def delete_joke(joke_id):
        joke = Joke.query.get(joke_id)
        if not joke:
            return jsonify({"error": "joke not found"}), 404

        user = current_user()
        if joke.user_id is not None and joke.user_id != user.id:
            return jsonify({"error": "not authorised"}), 403

        db.session.delete(joke)
        db.session.commit()
        return jsonify({"message": "deleted"}), 200

    # ---- External API Integration ----

    @app.get("/categories")
    @jwt_required()
    def categories():
        """Fetches categories from the external Chuck Norris API."""
        try:
            resp = requests.get(f"{CHUCK_API_BASE}/categories", timeout=5)
            resp.raise_for_status()
        except requests.RequestException:
            return jsonify({"error": "failed to fetch categories"}), 502

        return jsonify({"categories": resp.json()}), 200

    @app.get("/random")
    @jwt_required()
    def random_joke():
        """
        Fetches a random joke from the external API and saves it to the DB.
        Supports filtering by category query param.
        """
        user = current_user()

        selected_category = request.args.get("category")
        params = {"category": selected_category} if selected_category else None

        try:
            resp = requests.get(f"{CHUCK_API_BASE}/random", params=params, timeout=5)
            resp.raise_for_status()
        except requests.RequestException:
            return jsonify({"error": "failed to fetch joke from external API"}), 502

        data = resp.json()
        external_id = data.get("id")
        value = data.get("value")
        cats = data.get("categories") or []
        category = cats[0] if cats else None

        # Check if we already have this joke for this user
        existing = Joke.query.filter_by(joke_id=external_id, user_id=user.id).first()
        if existing:
            return jsonify(existing.to_dict()), 200

        # Save new joke
        joke = Joke(joke_id=external_id, value=value, category=category, user_id=user.id)
        db.session.add(joke)
        db.session.commit()
        return jsonify(joke.to_dict()), 201

    return app


if __name__ == "__main__":
    app = create_app()

    # Define SSL context for HTTPS (Option 2 requirement)
    # Using the local certs generated by mkcert
    ssl_context = ("cert.pem", "key.pem")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=os.environ.get("FLASK_DEBUG", "false").lower() in ("1", "true"),
        ssl_context=ssl_context,
    )