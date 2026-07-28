# Desafio de Travesias

Plataforma gamificada de trivias educativas y de entretenimiento.

## Stack

- **Backend**: FastAPI + PostgreSQL + Redis + Celery
- **Frontend**: React + TypeScript + Vite
- **Infra**: Railway

## Desarrollo

```bash
# Backend
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```
