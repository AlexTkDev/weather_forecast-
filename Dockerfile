FROM python:3.13-slim

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
       build-essential \
       postgresql-client \
       netcat-openbsd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
