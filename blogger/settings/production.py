from .base import *
import os

env = os.environ.copy()
SECRET_KEY = env['VIKAT_SECRET_KEY']

DEBUG = False

try:
    from .local import *
except ImportError:
    pass
