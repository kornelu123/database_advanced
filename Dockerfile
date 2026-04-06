FROM python:3.12-slim

WORKDIR /app

# Instalacja zależności systemowych (dla asyncpg, bcrypt itp.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Czekaj na bazę i uruchom seed, potem serwer
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

CMD ["/wait-for-it.sh", "db:5432", "--", "sh", "-c", "python data.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
