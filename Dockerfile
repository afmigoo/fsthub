FROM python:3-alpine3.22

RUN apk add gcc python3-dev musl-dev linux-headers

WORKDIR /fsthub

COPY src ./
COPY requirements.txt .

RUN pip install -r requirements.txt
