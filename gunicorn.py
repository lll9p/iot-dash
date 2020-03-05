# config.py
from .config import app_home, debug

debug = debug
loglevel = 'error'
bind = "127.0.0.1:8050"
chdir = app_home
pidfile = "/var/log/gunicorn/gunicorn.pid"
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/debug.log"
daemon = False
workers = 2
reload = True
x_forwarded_for_header = 'X-FORWARDED-FOR'
