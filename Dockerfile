FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt uvicorn==0.34.0

COPY src/ src/

FROM base AS runtime

EXPOSE 8000
CMD ["uvicorn", "rover.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM base AS test

COPY tests/ tests/

CMD ["pytest", "tests/", "-v", "--tb=short"]
