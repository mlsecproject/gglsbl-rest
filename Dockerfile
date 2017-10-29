FROM python:2.7-alpine3.6

## Create app directory
RUN mkdir -p /root/gglsbl-rest/db
WORKDIR /root/gglsbl-rest
ENV GSB_DB_DIR /root/gglsbl-rest/db
ENV LOGGING_CONFIG /root/gglsbl-rest/logging.conf

## Copy app files and initial GSB database
COPY ["requirements.txt", "*.py", "logging.conf", "./"]

# Install necessary OS and Python packages
RUN apk update && \
    apk upgrade && \
    pip install -r requirements.txt && \
    rm -rf /root/.cache/pip/* && \
    rm -rf /var/cache/apk/* && \
    rm -rf /tmp/* && \
    rm -rf /root/.cache/ && \
    crontab -l | { cat; echo "*/5   *   *   *   *   /usr/local/bin/python /root/gglsbl-rest/update.py"; } | crontab -

EXPOSE 5000

# Perform initial DB update, start crond for regular updates then start app.
ENTRYPOINT python update.py && crond -L /proc/1/fd/2 && gunicorn --config config.py --log-config ${LOGGING_CONFIG} app:app
