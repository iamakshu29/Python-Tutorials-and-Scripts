FROM python:3.11

LABEL "Author"="Akshat.V"
LABEL "Project"="URL Shortener"

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV POSTGRESQL_DATABASE_URL="postgresql://postgres:admin@db:5432/UrlShortenerDB"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]