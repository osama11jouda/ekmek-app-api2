import os
from datetime import timedelta

DEBUG = True
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = os.environ.get('APP_SECRET_KEY')
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
JWT_BLACKLIST_ENABLED = True
JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
UPLOADED_IMAGES_DEST = os.path.join('static', 'images')
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)

