import os

class Config:
    SECRET_KEY = open("instance/secret_key.txt").read().strip()
    SQLALCHEMY_DATABASE_URI = "sqlite:///sapcca.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "JWT_SECRET_123"  # change later to strong key
