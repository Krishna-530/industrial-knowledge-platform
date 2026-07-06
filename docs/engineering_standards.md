# Engineering Standards & Guidelines

This document outlines the professional software engineering standards, patterns, and principles to be followed throughout the development of the Industrial Knowledge Intelligence Platform.

## 1. Core Architectural Patterns

### Clean Architecture & Separation of Concerns
The application is structured into decoupled layers, ensuring business logic is isolated from web frameworks, UI frameworks, and database implementations:
- **Domain Layer (Entities/Models & Schemas)**: Plain old Python objects / Pydantic models declaring business shapes. Absolutely no external dependencies (like DB/ORM logic).
- **Application Layer (Services)**: Contains business workflows (e.g. document ingestion, graph generation). Orchestrates models and repositories.
- **Infrastructure Layer (Repositories & Clients)**: Implementation details such as Neo4j bolt driver, SQLAlchemy database queries, and pdfplumber parsing functions.
- **Presentation/API Layer (Routes & Views)**: API controllers (FastAPI routers) and UI modules (Next.js components) that format incoming/outgoing data.

### Repository Pattern & Dependency Injection
- All database operations must go through specialized repository classes (e.g., `DocumentRepository`, `EmbeddingRepository`).
- Framework controllers must not instantiate dependencies directly. FastAPI's Dependency Injection (`Depends()`) and class-based constructors must be used.

## 2. Naming Conventions

### Backend (Python)
- **Files & Modules**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions, Variables & Parameters**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`

### Frontend (TypeScript / React)
- **Components & Layouts**: `PascalCase.tsx`
- **Hooks**: `useCamelCase.ts`
- **Helpers & Utilities**: `camelCase.ts`

## 3. Logging & Error Handling Strategy

### Backend Logging
- Use structured logging (`structlog` or standard library mapped to JSON in production).
- Do not log raw user secrets, API keys, or raw parsed industrial document texts that may contain PII/sensitive operations data.

### Global Exception Handling
- Implement custom HTTP exceptions inheriting from a base API exception.
- Use a FastAPI middleware exception handler to intercept all unhandled exceptions, returning a clean standard JSON error response:
```json
{
  "error_code": "RESOURCE_NOT_FOUND",
  "message": "The requested document could not be found.",
  "details": {}
}
```

## 4. Git Branching & Commit Conventions

### Branching Strategy (Git Flow / GitHub Flow)
- `main`: Production-ready release branch.
- `develop`: Development integration branch.
- Feature branches: `feature/<ticket-id>-<short-description>`
- Bugfix branches: `bugfix/<ticket-id>-<short-description>`

### Semantic Commit Messages
Commits must follow the Conventional Commits specification:
- `feat`: A new feature (e.g., `feat: add pgvector document indexing`)
- `fix`: A bug fix (e.g., `fix: resolve OCR timeout on scanned PDFs`)
- `docs`: Documentation changes
- `style`: Formatting, missing semi-colons, etc. (no production code change)
- `refactor`: Refactoring production code without changing behavior
- `test`: Adding missing tests or correcting existing tests
- `chore`: Updating build tasks, package manager configs, etc.
