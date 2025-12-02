# MEGALAI Backend

Async FastAPI backend skeleton for the MEGALAI educational platform.

## Setup

1. **Python environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment variables**
   Copy `.env.example` to `.env` and update values.

4. **Run the app**
   ```bash
   uvicorn app.main:app --reload
   ```

## Notes

- JWT secrets, database URL, and other settings are loaded from `.env`.
- Async SQLAlchemy + asyncpg handle PostgreSQL access.
- AI endpoints under `/ai` return mocked data and can be replaced with real provider calls in `app/api/routes_ai.py`.
- Role-based access control helpers live in `app/api/deps.py`.
