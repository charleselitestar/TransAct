# app_config/config.py

import logging

class Config:
    STATIC_FOLDER = "static"
    OUTPUT_FOLDER = "documents"
    SECRET_KEY = "your_secret_key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///transact_data.db"
    UPLOAD_FOLDER = "uploads"
    UPLOADS_DEFAULT_DEST = "documents"
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = False

    # Flask-Mail Configuration
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = ""
    MAIL_PASSWORD = ""
    MAIL_DEFAULT_SENDER = "elite@docs.com"  # This is optional

    # Logging Configuration
    LOG_FILENAME = "app.log"
    LOG_LEVEL = logging.INFO

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(Config.LOG_LEVEL)

# Create file handler
file_handler = logging.FileHandler(Config.LOG_FILENAME)
file_handler.setLevel(Config.LOG_LEVEL)

# Create log format
log_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(log_format)

# Add file handler to logger
logger.addHandler(file_handler)