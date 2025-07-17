FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN apt update && apt install -y ffmpeg curl && \
    pip install flask yt-dlp pytube

EXPOSE 5000
CMD ["python", "main.py"]
