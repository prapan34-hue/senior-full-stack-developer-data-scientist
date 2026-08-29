# PostgreSQL + FastAPI

## Start

```powershell
docker compose up -d
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --port 8000
```

Open `http://localhost:8000/docs` and check `GET /api/health`.

For an existing PostgreSQL instance, run `schema.sql` with `psql` and update
`DATABASE_URL`. Keep credentials in `.env` or a secrets manager, never in source.

The application intentionally does not call `create_all()`. Schema changes
should be applied explicitly with SQL migrations (Alembic is recommended).
