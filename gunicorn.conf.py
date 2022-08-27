wsgi_app = "kvisualbot.wsgi"

worker_class = "gthread"
workers = 1
threads = 2
timeout = 30
graceful_timeout = 30
keepalive = 65

errorlog = "-"
accesslog = "-"
loglevel = "debug"
capture_output = True