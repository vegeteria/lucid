FROM python:3.11-slim

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY lucida-bin /usr/local/bin/lucida
RUN chmod +x /usr/local/bin/lucida

COPY bot/ ./bot/

CMD ["python", "-m", "bot.main"]
