from os import environ

import logging.config
from apscheduler.schedulers.background import BackgroundScheduler
from multiprocessing import cpu_count
from subprocess import Popen

logging.config.fileConfig('logging.conf')

bind = "0.0.0.0:5000"
workers = int(environ.get('WORKERS', cpu_count() * 8 + 1))
timeout = int(environ.get('TIMEOUT', 120))
access_log_format = '%(h)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" "%({X-Forwarded-For}i)s" "%({X-Forwarded-Port}i)s" "%({X-Forwarded-Proto}i)s"  "%({X-Amzn-Trace-Id}i)s"'
max_requests = int(environ.get('MAX_REQUESTS', 16384))
limit_request_line = int(environ.get('LIMIT_REQUEST_LINE', 8190))
keepalive = int(environ.get('KEEPALIVE', 60))

log = logging.getLogger(__name__)


def update():
    log.info("Starting update process...")
    po = Popen("python update.py", shell=True)
    log.info("Update started as PID %d", po.pid)
    rc = po.wait()
    log.info("Update process finished with status code %d", rc)


def on_starting(server):
    log.info("Initial database load...")
    po = Popen("python update.py", shell=True)
    log.info("Update started as PID %d", po.pid)
    rc = po.wait()
    log.info("Update process finished with status code %d", rc)

    log.info("Starting scheduler...")
    sched = BackgroundScheduler(timezone="UTC")
    sched.start()
    sched.add_job(update, id="update", coalesce=True, max_instances=1, trigger='interval', minutes=30)
