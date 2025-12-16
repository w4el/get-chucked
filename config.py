import os
from pathlib import Path
from dotenv import load_dotenv

# Always load .env when running via `python app.py`
load_dotenv()

class Config:
    """Application configuration loaded from environment variables."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-please")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "another-secret")
    FLASK_HTTPS = os.environ.get("FLASK_HTTPS", "false").lower()

def get_ssl_context():
    """
    Determine which SSL context to use.
    Prioritizes env vars, then local files, then adhoc.
    """
    cert_path = os.environ.get("SSL_CERT")
    key_path = os.environ.get("SSL_KEY")
    if cert_path and key_path:
        return (cert_path, key_path)

    root = Path.cwd()
    cert_file = root / "cert.pem"
    key_file = root / "key.pem"
    
    # Use local certs if they exist
    if cert_file.exists() and key_file.exists():
        return (str(cert_file), str(key_file))

    https_mode = os.environ.get("FLASK_HTTPS", "").lower()
    if https_mode in ("true", "adhoc"):
        return "adhoc"

    return None