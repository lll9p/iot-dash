# config.py

debug = False
loglevel = 'error'
bind = "0.0.0.0:8050"
chdir = "/home/lao/data/monitor-dash"
pidfile = "/var/log/gunicorn/gunicorn.pid"
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/debug.log"
daemon = False
workers = 2
reload = True
x_forwarded_for_header = 'X-FORWARDED-FOR'
