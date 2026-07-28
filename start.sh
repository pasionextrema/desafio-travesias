#!/bin/bash
echo "=== Desafio de Travesias v1.0 ==="
echo "PORT: ${PORT:-8000}"
echo "DATABASE_URL set: $(if [ -n \"${DATABASE_URL}\" ]; then echo 'YES'; else echo 'NO'; fi)"
echo "Starting uvicorn..."
exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}" --log-level info
