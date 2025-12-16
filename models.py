from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    """Simple user model with hashed password storage."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    # One-to-many: a user can have multiple jokes.
    jokes = db.relationship("Joke", backref="author", lazy=True)

    def set_password(self, password):
        """Hash and store a password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Validate a password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class Joke(db.Model):
    """A joke stored in the database."""
    __tablename__ = "jokes"
    __table_args__ = (
        db.UniqueConstraint("joke_id", "user_id", name="uq_jokes_joke_id_user_id"),
    )

    id = db.Column(db.Integer, primary_key=True)
    # External API joke ID (null for user-submitted jokes)
    joke_id = db.Column(db.String(64), index=True, nullable=True)
    value = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Nullable: external jokes are not "authored" by a local user.
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    
    def to_dict(self):
        """Dictionary representation for API responses."""
        return {
            "id": self.id,
            "joke_id": self.joke_id,
            "value": self.value,
            "category": self.category,
            "created_at": self.created_at.isoformat(),
            "user": self.author.username if self.author else None,
        }

    def __repr__(self):
        return f"<Joke {self.joke_id or self.id}>"