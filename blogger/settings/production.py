from .base import *

SECRET_KEY = 'al5*^^_$*$l0xo36)4f6!rku)024z(&d0kt%id5=5(pdryoxe_'

ALLOWED_HOSTS = ['vikatakavi.info', '*.vikatakavi.info']

DEBUG = True

try:
    from .local import *
except ImportError:
    pass
