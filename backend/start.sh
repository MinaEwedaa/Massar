#!/bin/bash
set -e
# Railway sets PORT automatically, ensure it's used correctly
# Default to 8000 if PORT is not set
PORT=${PORT:-8000}
# Convert to integer (removes any whitespace or non-numeric characters)
PORT=$((PORT + 0))
# Validate port range
if [ "$PORT" -lt 1 ] || [ "$PORT" -gt 65535 ]; then
  echo "Warning: Invalid PORT value, using default 8000"
  PORT=8000
fi
echo "Starting server on port $PORT"
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"

