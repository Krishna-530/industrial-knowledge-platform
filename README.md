# Industrial Knowledge Intelligence Platform
> AI-Powered Asset & Operations Brain

This repository contains the foundational structure for the Industrial Knowledge Intelligence Platform, designed to ingest complex industrial documents (SOPs, manuals, logs) and transform them into a queryable semantic Knowledge Graph.

---

## 1. Project Map

```text
industrial-knowledge-platform/
├── backend/                  # FastAPI Application
│   ├── app/                  # Main code base
│   │   ├── api/              # API Route Handlers
│   │   ├── core/             # Settings, configurations
│   │   ├── models/           # SQLAlchemy Data Models
│   │   ├── repositories/     # Data Access Layer
│   │   ├── schemas/          # Pydantic Schemas
│   │   └── services/         # Business Logic (RAG, Graph, Processing)
│   ├── tests/                # Pytest Test Suites
│   ├── pyproject.toml        # Poetry Dependencies
│   └── alembic.ini           # Alembic Database Migration Configuration
├── frontend/                 # Next.js App Router Client
│   ├── app/                  # Next.js Pages & Layouts
│   ├── components/           # Generic Reusable Components
│   ├── features/             # Feature-based Components (Chat, Graph)
│   ├── styles/               # Tailwind & Global CSS
│   └── package.json          # Node Modules & Scripts
├── database/                 # Database Migrations & Schemas
│   ├── migrations/           # Alembic Migration Scripts
│   ├── neo4j/                # Graph Seeding & Scripts
│   └── postgres/             # Relation & Vector Initialization
├── docs/                     # Architectural & Engineering Documentation
│   ├── architecture.md       # High-level Design & Data Flows
│   └── engineering_standards.md # Code quality & Linting standards
└── docker-compose.yml        # Development Services (Postgres, Neo4j)
```

---

## 2. Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+

### Setup Steps
1. **Clone the repository** and navigate to the directory:
   ```bash
   cd industrial-knowledge-platform
   ```

2. **Start Datastores via Docker Compose**:
   ```bash
   docker-compose up -d
   ```
   This will spin up:
   - PostgreSQL (port `5432`) containing the `pgvector` extension.
   - Neo4j (port `7474` for browser GUI, `7687` for bolt protocol).

3. **Backend Setup**:
   ```bash
   cd backend
   pip install poetry
   poetry install
   poetry run uvicorn app.main:app --reload
   ```
   The backend documentation will be accessible at [http://localhost:8000/docs](http://localhost:8000/docs).

4. **Frontend Setup**:
   ```bash
   cd ../frontend
   npm install
   npm run dev
   ```
   The web portal will run on [http://localhost:3000](http://localhost:3000).
