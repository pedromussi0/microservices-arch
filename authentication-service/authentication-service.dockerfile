FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

ENV ALEMBIC_CONFIG=/app/alembic.ini

EXPOSE 8000

CMD ["sh", "-c", "/wait-for-it.sh -t 3 db:5432 -- alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
