FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/app ./app
COPY backend/model ./model
RUN mkdir -p data

# Copy start script
COPY backend/start.sh ./start.sh
RUN chmod +x ./start.sh

EXPOSE 8000

# Use the start script which properly handles PORT environment variable
# Use shell form to ensure environment variables are expanded
CMD ./start.sh



