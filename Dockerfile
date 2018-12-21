FROM alpine:3.8

# Install necessary OS packages and create non-root user for service
RUN apk update && \
    apk upgrade && \
    apk add -u python py2-pip && \
    adduser -D -s /sbin/nologin gglsbl

## Populate app directory
WORKDIR /home/gglsbl
ENV GSB_DB_DIR /home/gglsbl/db
COPY ["requirements.txt", "*.py", "logging.conf", "./"]
ENV LOGGING_CONFIG /home/gglsbl/logging.conf

# Install Python packages, cleanup, set permissions and configure crontab
RUN pip install --upgrade pip setuptools && \
    pip install -r requirements.txt && \
    rm -rf /root/.cache/pip/* && \
    rm -rf /var/cache/apk/* && \
    rm -rf /tmp/* && \
    rm -rf /root/.cache/ && \
    mkdir -p $GSB_DB_DIR && \
    chown -R gglsbl:gglsbl *

USER gglsbl:gglsbl

EXPOSE 5000

# Perform initial DB update, start crond for regular updates then start app.
ENTRYPOINT exec gunicorn --config config.py --log-config ${LOGGING_CONFIG} app:app
