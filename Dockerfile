FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libheif-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app .

RUN ls -R /app
RUN pwd

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9240", "--reload"]