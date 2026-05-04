FROM python:3.12-slim

WORKDIR /app

ENV APP_VERSION=dev
ENV IMAGE_TAG=local
ENV DB_PATH=/data/tasks.db

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app.main:app"]
