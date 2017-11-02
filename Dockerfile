FROM python:2.7-alpine3.6

# Install necessary OS and Python packages
RUN apk update && \
    apk upgrade && \
    apk add su-exec && \
    adduser -D -s /sbin/nologin gglsbl

## Populate app directory
WORKDIR /home/gglsbl
ENV GSB_DB_DIR /home/gglsbl/db
COPY ["requirements.txt", "*.py", "logging.conf", "./"]
ENV LOGGING_CONFIG /home/gglsbl/logging.conf

RUN pip install -r requirements.txt && \
    rm -rf /root/.cache/pip/* && \
    rm -rf /var/cache/apk/* && \
    rm -rf /tmp/* && \
    rm -rf /root/.cache/ && \
    mkdir -p $GSB_DB_DIR && \
    chown -R gglsbl:gglsbl * && \
    crontab -l | { cat; echo "*/5   *   *   *   *   /sbin/su-exec gglsbl:gglsbl /usr/local/bin/python /home/gglsbl/update.py"; } | crontab -

EXPOSE 5000

# Perform initial DB update, start crond for regular updates then start app.
ENTRYPOINT  chmod 777 /proc/1/fd && \
            chmod 777 /proc/1/fd/1 && \
            chmod 777 /proc/1/fd/2 && \
            su --group=gglsbl gglsbl python update.py && \
            crond -L /proc/1/fd/2 && \
            /sbin/su-exec gglsbl:gglsbl gunicorn --config config.py --log-config ${LOGGING_CONFIG} app:app
