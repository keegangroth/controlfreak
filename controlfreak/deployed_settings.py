import os
import json

try:
    from .settings import *
except ImportError:
    pass

DEBUG = False

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

SECRET_KEY = json.loads(os.environ['SECRET_KEY'])['SECRET_KEY']

rds_config = json.loads(os.environ['RDS_CREDENTIALS'])
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.' + rds_config['engine'],
        'HOST': rds_config['host'],
        'PORT': rds_config['port'],
        'USER': rds_config['username'],
        'PASSWORD': rds_config['password'],
        'NAME': rds_config['dbname'],
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
