FROM python:3.12-slim

WORKDIR /app

ENV APP_VERSION=dev
ENV IMAGE_TAG=local

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8000

CMD ["python", "-m", "app.main"]
