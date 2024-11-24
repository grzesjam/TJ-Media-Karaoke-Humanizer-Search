FROM python:3.12
RUN adduser --system --disabled-password --group worker
WORKDIR /app


COPY requirements.txt .
RUN pip install -r requirements.txt


COPY ui/ /app/ui/
COPY main.py /app/

RUN mkdir /app/cache
RUN chown -R worker:worker /app/cache
USER worker

ENTRYPOINT fastapi run