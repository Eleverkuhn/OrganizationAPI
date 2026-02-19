FROM python:3.14.2-slim

WORKDIR /app

COPY pyproject.toml .
COPY uv.lock .

RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir .

COPY . .

EXPOSE 8000
