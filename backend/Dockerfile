FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/app ./app
COPY backend/model ./model
RUN mkdir -p data

EXPOSE 8000

# Use PORT environment variable if provided, otherwise default to 8000
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}



