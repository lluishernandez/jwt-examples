FROM python:3.6-alpine

ADD Dockerfile /Dockerfile
ADD requirements.txt /requirements
ADD private_key /key

RUN apk add --no-cache libffi-dev build-base python3-dev openssl-dev && \
    pip install -r requirements && \
    mkdir -p /opt/example && \
    apk del libffi-dev build-base python3-dev openssl-dev

ADD jwt_issuer.py /opt/example/jwt_issuer

EXPOSE 5000

CMD ["python", "/opt/example/jwt_issuer"]
