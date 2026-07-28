#!/bin/bash
echo "=== Desafio de Travesias ==="
echo "PORT: ${PORT:-8000}"
echo "DATABASE_URL set: $(if [ -n \"${DATABASE_URL}\" ]; then echo 'YES'; else echo 'NO'; fi)"
echo "DATABASE_PRIVATE_URL set: $(if [ -n \"${DATABASE_PRIVATE_URL}\" ]; then echo 'YES'; else echo 'NO'; fi)"
echo "REDIS_URL set: $(if [ -n \"${REDIS_URL}\" ]; then echo 'YES'; else echo 'NO'; fi)"
echo "SECRET_KEY set: $(if [ -n \"${SECRET_KEY}\" ]; then echo 'YES'; else echo 'NO'; fi)"
echo "Starting uvicorn..."
exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}" --log-level info
