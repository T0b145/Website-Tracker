# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

# Copy project files
COPY . /app

EXPOSE 5000
ENV FLASK_ENV=production

# Run the Flask app via gunicorn
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "web.server:app"] 