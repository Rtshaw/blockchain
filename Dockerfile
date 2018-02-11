FROM python:3.6-alpine

WORKDIR /app

ENV BUILD_LIST git

RUN apk add --update $BUILD_LIST \
    && git clone https://github.com/Rtshaw/blockchain.git /app \
    && pip3 install pipenv \
    && pipenv --python=python3.6 \
    && pipenv install \
    && apk del $BUILD_LIST \
    && rm -rf /var/cache/apk/*

EXPOSE 5000

ENTRYPOINT [ "pipenv", "run", "python3", "/app/musicblockchain.py", "--port", "5000"  ]
