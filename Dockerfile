# Stage 1: Build the Rust binary
FROM rust:1.82-slim as builder
RUN apt-get update && apt-get install -y git build-essential pkg-config libssl-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /usr/src/app
RUN git clone https://github.com/jelni/lucida-downloader.git .
RUN cargo build --release

# Stage 2: Final Python Image
FROM python:3.11-slim

RUN apt-get -o Acquire::ForceIPv4=true update && apt-get -o Acquire::ForceIPv4=true install -y ffmpeg gcc python3-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the compiled binary from the builder stage
COPY --from=builder /usr/src/app/target/release/lucida /usr/local/bin/lucida
RUN chmod +x /usr/local/bin/lucida

COPY bot/ ./bot/

CMD ["python", "-m", "bot.main"]
