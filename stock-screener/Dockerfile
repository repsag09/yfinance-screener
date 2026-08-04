# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system deps if needed (uncomment if you have extra system packages)
# RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY stock-screener/requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip
RUN pip install -r /app/requirements.txt

# Copy repository files
COPY . /app

# Default environment variables (can be overridden in relays.app UI)
ENV SCAN_PATH=stock-screener/stocks_scan.csv
ENV RUN_REAL=false
ENV PAPER_CAPITAL=5000
ENV POSITION_PCT=0.10
ENV APCA_API_BASE_URL=https://paper-api.alpaca.markets

# Use the relays entrypoint; relays.app can call the handler or run the file directly
CMD ["python", "stock-screener/relays_entry.py"]
