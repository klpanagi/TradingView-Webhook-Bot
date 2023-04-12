FROM python:3.9-alpine
LABEL Auther="fabston"
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN apk add gcc python3-dev openssl-dev musl-dev libffi-dev &&\
    pip install --no-cache-dir -r requirements.txt

COPY main.py handler.py config.py ./
EXPOSE 8080

CMD [ "uvicorn", "main:app", "--port", "8080", "--host", "0.0.0.0" ]