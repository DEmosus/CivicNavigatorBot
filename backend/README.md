# CivicNavigator Backend

Backend service for CivicNavigator, a civic engagement platform that enables residents to report incidents, access knowledge, and interact with AI‑powered services. Built with FastAPI, SQLModel/SQLAlchemy, and JWT authentication, containerized with Docker, and production‑ready with observability, linting, and CI/CD.

## 🚀 Features

- **FastAPI REST API** with automatic docs (`/docs`).
- **Authentication** with JWT (login, register, token refresh).
- **Incident reporting** endpoints (CRUD).
- **Knowledge base** with embeddings (via sentence-transformers).
- **Observability**:
  - Structured request logging.
  - `/health` endpoint.
  - `/metrics` endpoint (Prometheus).
  - Optional Sentry integration.
- **Deployment ready**:
  - Dockerfile (Gunicorn + Uvicorn workers).
  - `.env.template` for environment variables.
  - CI/CD with GitHub Actions.
  - Pre‑commit hooks for linting, formatting, type checking.

## 📦 Tech Stack

- **Framework**: FastAPI (Starlette + Pydantic v2)
- **Database**: SQLModel (SQLAlchemy + Pydantic)
- **Auth**: JWT via python-jose, passlib[bcrypt]
- **ML/Embeddings**: sentence-transformers, scikit-learn
- **Monitoring**: Sentry SDK, Prometheus Instrumentator
- **Containerization**: Docker
- **Tooling**: Black, isort, Ruff, Mypy, Pytest, Pre‑commit

## ⚙️ Setup

1. **Clone the repo**
   ```bash
   git clone https://github.com/your-org/civicnavigator-backend.git
   cd civicnavigator-backend
   ```
2. **Create environment file**
   Copy `.env.template` → `.env` and fill in values:
   ```bash
   cp .env.template .env
   ```
   Key variables:
   ```
   ENV=development|production
   DATABASE_URL=postgresql+psycopg://user:pass@host:5432/dbname
   JWT_SECRET_KEY=your-secret
   CORS_ORIGINS=http://localhost:5173
   SENTRY_DSN=optional
   ```
3. **Install dependencies (dev)**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements-dev.txt
   ```
4. **Run locally**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
   Visit:
   - API docs → http://localhost:8000/docs
   - Health check → http://localhost:8000/health
   - Metrics → http://localhost:8000/metrics

## 🐳 Docker

**Build**

```bash
docker build -t civicnavigator:latest .
```

**Run**

```bash
docker run --env-file .env -p 8000:8000 civicnavigator:latest
```

## 🧪 Testing

Run tests with coverage:

```bash
pytest --maxfail=1 --disable-warnings -q --cov=.
```

## 🛡️ Code Quality

This project enforces strict linting, formatting, and typing.

**Pre‑commit hooks**
Install once:

```bash
pre-commit install
```

Run on all files:

```bash
pre-commit run --all-files
```

**Tools**:

- Black (formatting)
- isort (imports)
- Ruff (linting, autofix)
- Mypy (type checking)

## 🔄 CI/CD

GitHub Actions workflow (`.github/workflows/ci.yml`) runs on every push/PR:

- Pre‑commit hooks
- Mypy type checking
- Pytest with coverage

## 📈 Observability

- `/health` → service status
- `/metrics` → Prometheus metrics
- Sentry integration (set `SENTRY_DSN` in `.env`)

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch
3. Run pre‑commit hooks locally
4. Submit a PR

## 📜 License

MIT License
