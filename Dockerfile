FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN apt-get update && \
    apt-get install -y ffmpeg curl gnupg && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    pip install --no-cache-dir -r requirements.txt

CMD ["gunicorn", "-b", "0.0.0.0:5000", "main:app"]
