FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ backend/
COPY main.py .
COPY start.sh .

RUN chmod +x start.sh

EXPOSE 8000

CMD ["./start.sh"]
