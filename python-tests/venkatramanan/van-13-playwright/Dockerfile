FROM mcr.microsoft.com/playwright/python:v1.49.0-noble

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV HEADLESS=1

COPY requirements.txt .

RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt

COPY test.py .

CMD ["python", "test.py"]