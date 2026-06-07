FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DB_URI=postgresql://neondb_owner:npg_el79zPcUZSCs@ep-empty-sky-a104qhds-pooler.ap-southeast-1.aws.neon.tech/post?sslmode=require&channel_binding=require \
    FLASK_KEY=8BYkEfBA6O6donzWlSihBXOx7c0sKR6b \
    SENDER_EMAIL=alliyantesting@gmail.com \
    SENDER_PASSWORD=iobtgvkrtucupmtm \
    RECIPIENT_EMAIL=alliyan002@gmail.com

# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "--threads", "2", "--timeout", "120", "main:app"]
