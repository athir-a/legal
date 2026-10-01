# Verified Legal Research Assistant

## Local and Demo Setup

Python 3.10+, Node.js, MySQL 8, and the project dependencies are required. From the repository root, create a private `.env` using `.env.example` as a template. Keep `DJANGO_DEBUG=1` for local development. For the hackathon runtime, configure `USE_MYSQL=1` and a MySQL account with access to the `legal_rag` database. Do not use the example password or a root account in a deployed environment.

The backend loads the root `.env`. With `USE_MYSQL=1`, it requires `MYSQL_DATABASE`, `MYSQL_USER`, and `MYSQL_PASSWORD`; host and port default to `127.0.0.1:3306`. Without `USE_MYSQL`, only local development uses SQLite. Production (`DJANGO_DEBUG=0`) requires `DJANGO_SECRET_KEY` and an explicit `DJANGO_ALLOWED_HOSTS` list.

Create the MySQL database and least-privilege account using your MySQL administrator, then grant that account access to the application database. Install and migrate from `backend/`:

```sql
CREATE DATABASE legal_rag CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'legal_app'@'localhost' IDENTIFIED BY 'use-a-generated-password';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX, DROP
ON legal_rag.* TO 'legal_app'@'localhost';
FLUSH PRIVILEGES;
```

The account needs schema privileges for Django migrations. Restrict the account host and privileges to the deployment environment where possible.

```powershell
.\.venv311\Scripts\python.exe -m pip install -r requirements.txt
.\.venv311\Scripts\python.exe manage.py migrate
.\.venv311\Scripts\python.exe manage.py showmigrations legaldata
```

The migrations create `LegalDocument`, `LegalChunk`, `ChatSession`, and `ChatMessage`. The corpus importer and chunker are available if a fresh database needs corpus data:

```powershell
.\.venv311\Scripts\python.exe manage.py import_consumer_act
.\.venv311\Scripts\python.exe manage.py create_chunks
```

Put the Gemini key in the ignored `agent/.env` file using `agent/.env.example` as a template. The application retains the bounded Gemini attempt and local fallback when the model is unavailable.

Run Django from `backend/`:

```powershell
.\.venv311\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

The endpoint is `POST /api/ask/`. The optional `session_id` returned by one response can be sent on the next request to continue that conversation. Recent turns are loaded from the database and provided as context; the legal tools must still verify current claims.

## Frontend

From `frontend/`, install and run Vite:

```powershell
npm ci
npm run dev
```

The development proxy forwards `/api` to `http://localhost:8000` by default. To use another local backend, set `API_PROXY_TARGET`, for example `http://127.0.0.1:8001`.

Build and check the frontend:

```powershell
npm run lint
npm run build
```

For deployment, serve the built frontend and proxy `/api/` to Django on the same origin. This avoids requiring cross-origin browser access. Run Django behind a production WSGI/ASGI server and TLS reverse proxy; do not use `runserver` in production. Set `DJANGO_DEBUG=0`, a generated `DJANGO_SECRET_KEY`, allowed hosts, CSRF trusted origins as needed, and MySQL credentials through environment variables. Run `collectstatic` if serving Django admin assets.

## Verification

Run backend tests from `backend/`:

```powershell
.\.venv311\Scripts\python.exe manage.py test
```

Run the real 20-question HTTP benchmark while Django is running:

```powershell
.\.venv311\Scripts\python.exe evaluation\endpoint_benchmark.py
```

The benchmark report and raw data are in `evaluation/results/latest.json`.
