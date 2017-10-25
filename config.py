from multiprocessing import cpu_count
from os import environ

bind = "0.0.0.0:5000"
workers = int(environ.get('WORKERS', cpu_count() * 2 + 1))
timeout = int(environ.get('TIMEOUT', 120))
access_log_format='%(h)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" "%({X-Forwarded-For}i)s" "%({X-Forwarded-Port}i)s" "%({X-Forwarded-Proto}i)s"  "%({X-Amzn-Trace-Id}i)s"'
max_requests = int(environ.get('MAX_REQUESTS', 16384))
