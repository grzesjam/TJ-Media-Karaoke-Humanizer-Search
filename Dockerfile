FROM python:3.12
WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ui/ main.py /app/

ENTRYPOINT fastapi run