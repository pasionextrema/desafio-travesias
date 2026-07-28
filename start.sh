#!/bin/bash
set -e

echo "Running database migrations..."
cd backend && alembic upgrade head && cd ..

echo "Starting server..."
exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}"
