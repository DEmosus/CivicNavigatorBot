# 🌍 CivicNavigator – Full Stack

CivicNavigator is a civic engagement platform where residents can report incidents, chat with a civic bot, and staff can manage and respond to reports. This repository contains both the **frontend** (React + Vite + TypeScript) and **backend** (FastAPI + SQLModel + JWT) services, plus Docker Compose for local development.

---

## 🚀 Features

- **Residents**

  - Chat with an AI‑powered civic bot
  - Report incidents (road maintenance, waste management, water supply, etc.)
  - Track incident status

- **Staff**

  - Manage incidents (view, update status, add notes)
  - Search knowledge base

- **Platform**
  - JWT authentication (register/login)
  - REST API with OpenAPI docs
  - Observability: `/health`, `/metrics` (Prometheus)
  - Containerized with Docker

---

## 📂 Project Structure

```
civicnavigator/
  frontend/               # React 19 + Vite + TS + Tailwind
  backend/                # FastAPI + SQLModel + JWT
  infra/
    docker-compose.yml    # Docker Compose for local dev
    nginx.conf            # Optional reverse proxy
  .env                    # Shared environment variables
```

---

## 🖥️ Frontend

**Tech stack:** React 19, TypeScript, Vite, Tailwind CSS, Axios, Vitest, ESLint/Prettier.

### Setup

```bash
cd frontend
npm install
npm run dev
```

**Environment variables** (`frontend/.env`):

```
VITE_API_BASE_URL=http://127.0.0.1:8000
```

**Build**

```bash
npm run build
```

---

## ⚙️ Backend

**Tech stack:** FastAPI, SQLModel/SQLAlchemy, JWT (python‑jose), passlib, Prometheus, Sentry (optional).

### Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Environment variables** (`backend/.env`):

```
ENV=development
DATABASE_URL=sqlite:///./civic.db
JWT_SECRET_KEY=replace-me
CORS_ORIGINS=http://localhost:5173
```

### Endpoints

**Auth**

- `POST /api/auth/register` → Register user
- `POST /api/auth/login` → Login, returns JWT

**Chat**

- `POST /api/chat/message` → Send message to civic bot

**Incidents**

- `POST /api/incidents` → Create incident
- `GET /api/incidents/{id}/status` → Get incident status

**Staff**

- `GET /api/staff/incidents` → List incidents (auth required)
- `PATCH /api/staff/incidents/{id}` → Update incident

**Knowledge Base**

- `GET /api/kb/search?q=...` → Search KB
- `POST /api/kb/index` → Add KB entry

**System**

- `GET /health` → Health check
- `GET /metrics` → Prometheus metrics

**Interactive docs:** http://localhost:8000/docs

---

## 🐳 Docker Compose

For full stack development:

```bash
cd infra
docker-compose up --build
```

- **Frontend** → http://localhost:5173
- **Backend** → http://localhost:8000

---

## 🧪 Testing

**Frontend:**

```bash
cd frontend
npx vitest run
```

**Backend:**

```bash
cd backend
pytest --maxfail=1 --disable-warnings -q --cov=.
```

---

## 👥 Roles

- **Resident:** Chat, report incidents, check status
- **Staff:** Manage incidents, search KB

---

## 🛡️ Code Quality

- **Frontend:** ESLint, Prettier, TypeScript strict mode
- **Backend:** Black, isort, Ruff, Mypy, Pytest
- Pre‑commit hooks for linting/formatting/type checking

---

## 📈 Observability

- `/health` → Service status
- `/metrics` → Prometheus metrics
- Optional Sentry integration (`SENTRY_DSN` in `.env`)

---

## 🔄 CI/CD

GitHub Actions workflow runs:

- Linting & formatting
- Type checking
- Tests with coverage

---

## 📜 License

MIT License
