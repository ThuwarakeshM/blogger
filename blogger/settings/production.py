from .base import *
import os

env = os.environ.copy()
SECRET_KEY = env['VIKAT_SECRET_KEY']

ALLOWED_HOSTS = ['vikatakavi.info', '*.vikatakavi.info'] 

DEBUG = False

try:
    from .local import *
except ImportError:
    pass
