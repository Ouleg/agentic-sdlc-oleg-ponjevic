FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

# Dependencies first: this layer is cached until requirements.txt changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Source and tests change most often, so they are copied last
COPY src/ src/
COPY tests/ tests/

CMD ["pytest", "tests/", "-v", "--tb=short"]
