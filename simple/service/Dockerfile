FROM python:3.6-alpine

ADD Dockerfile /Dockerfile
ADD requirements.txt /requirements
ADD public_key.pub /key.pub

RUN apk add --no-cache libffi-dev build-base python3-dev openssl-dev && \
    pip install -r requirements && \
    mkdir -p /opt/example && \
    apk del libffi-dev build-base python3-dev openssl-dev

ADD protected_service.py /opt/example/service

EXPOSE 5000

CMD ["python", "/opt/example/service"]
