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
   Copy `.env.example` to `.env` and update values. For hosted deployments (e.g., Render), set these environment variables directly:
   - `DATABASE_URL` (e.g., `postgresql+asyncpg://user:pass@host:5432/dbname`)
   - `JWT_SECRET_KEY`
   - `JWT_REFRESH_SECRET_KEY`
   - `JWT_ALGORITHM` (defaults to `HS256` if omitted)
   - `ACCESS_TOKEN_EXPIRE_MINUTES` (optional, defaults to 15)
   - `REFRESH_TOKEN_EXPIRE_DAYS` (optional, defaults to 30)
   - `ALLOWED_ORIGINS` (JSON array of origins, e.g., `["http://localhost:5173","https://megalai-frontend.netlify.app"]`)
   - `ENABLE_DOMAIN_RESTRICTION` (`true`/`false`)
   - `DEFAULT_ALLOWED_DOMAINS` (JSON array of allowed domains when restriction is enabled)

4. **Run the app**
   ```bash
   uvicorn app.main:app --reload
   ```

## Notes

- JWT secrets, database URL, and other settings are loaded from `.env`.
- Async SQLAlchemy + asyncpg handle PostgreSQL access.
- AI endpoints under `/ai` return mocked data and can be replaced with real provider calls in `app/api/routes_ai.py`.
- Role-based access control helpers live in `app/api/deps.py`.
