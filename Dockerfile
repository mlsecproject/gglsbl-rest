FROM alpine:3.13.5

# Install necessary OS packages and create non-root user for service
RUN apk update && \
    apk upgrade && \
    apk add -u python3 py3-pip py3-setuptools py3-wheel py3-multidict py3-yarl py3-flask py3-gunicorn && \
    adduser -D -s /sbin/nologin gglsbl

## Populate app directory
WORKDIR /home/gglsbl
ENV GSB_DB_DIR /home/gglsbl/db
COPY ["requirements.txt", "./"]
ENV LOGGING_CONFIG /home/gglsbl/logging.conf

# Install Python packages, cleanup and set permissions
RUN pip3 install -r requirements.txt && \
    rm -rf /root/.cache/pip/* && \
    rm -rf /var/cache/apk/* && \
    rm -rf /tmp/* && \
    rm -rf /root/.cache/ && \
    mkdir -p $GSB_DB_DIR && \
    chown -R gglsbl:gglsbl *

# CVE-2019-5021
RUN sed -i -e 's/^root::/root:!:/' /etc/shadow

# Run as a non-root user for security
USER gglsbl:gglsbl

EXPOSE 5000

COPY ["*.py", "logging.conf", "./"]

# Start app
ENTRYPOINT exec gunicorn --config config.py --log-config ${LOGGING_CONFIG} app:app
