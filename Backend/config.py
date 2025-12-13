import os

class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    try:
        SECRET_KEY = open(os.path.join(BASE_DIR, "instance", "secret_key.txt")).read().strip()
    except:
        SECRET_KEY = "dev_secret"  # Fallback for dev/CI if file missing
    SQLALCHEMY_DATABASE_URI = "sqlite:///sapcca.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "JWT_SECRET_123"  # change later to strong key
