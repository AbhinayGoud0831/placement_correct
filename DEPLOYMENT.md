# Deployment Guide

This guide covers deploying the platform beyond local development.

## Production Checklist

- [ ] Use strong `SECRET_KEY` in backend/.env (at least 32 random characters)
- [ ] Set `ACCESS_TOKEN_EXPIRE_MINUTES` to a reasonable value (e.g., 1440 = 24 hours)
- [ ] Move PostgreSQL to a managed database (AWS RDS, Heroku Postgres, etc.)
- [ ] Update `DATABASE_URL` to the production database
- [ ] Set `REACT_APP_API_BASE` to your backend domain in frontend/.env
- [ ] Remove `--reload` from uvicorn command (production should run via gunicorn or similar)
- [ ] Set up HTTPS/SSL for both frontend and backend
- [ ] Run `npm run build` for the frontend before deployment
- [ ] Test the full flow: upload resume, paste JD, run analysis, check history

## Local Ollama vs. Remote

By default, Ollama runs locally (`http://localhost:11434`). For production:
- **Option 1**: Run Ollama on a separate machine and set `OLLAMA_HOST` to its IP/domain
- **Option 2**: Use a managed LLM API instead of Ollama (modify `app/services/llm_extraction.py`)
- **Option 3**: Pre-compute embeddings and store them instead of calling Ollama on demand

## Database Backups

- Set up automated backups for PostgreSQL
- Resume files are stored on disk in `UPLOAD_DIR` — ensure regular backups

## Monitoring

- Monitor API latency, especially `/api/analyses` (calls Ollama + sentence-transformers)
- Log student analyses to audit trail
- Set alerts for high error rates

## Environment Variables (Production Example)

```env
DATABASE_URL=postgresql://user:password@prod-db.example.com:5432/placement_db
SECRET_KEY=<32-char-random-string>
OLLAMA_HOST=http://ollama-server.internal:11434
REACT_APP_API_BASE=https://api.placement.example.com
```
