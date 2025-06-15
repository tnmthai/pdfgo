# Dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . .

RUN apt-get update && apt-get install -y poppler-utils

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080
ENV PORT 8080

CMD ["python", "app.py"]
