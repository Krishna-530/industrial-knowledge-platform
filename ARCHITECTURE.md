# Phase 1 Architecture Documentation

## Overview

This document describes the architecture and design decisions for Phase 1 of the Industrial Knowledge Intelligence Platform backend.

## Project Goal

Build a production-ready, scalable FastAPI foundation that:
- Requires zero business logic
- Is ready for Phase 2 (database integration, services, repositories)
- Follows SOLID principles and Clean Architecture
- Uses dependency injection for testability
- Implements proper logging and error handling

## Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│                    API LAYER                            │
│  GET /api/v1/health  (Endpoints)                        │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────┐
│                  MIDDLEWARE LAYER                       │
│  CORS │ TrustedHost │ RequestID │ Timing │ ErrorHandler │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────┐
│                DEPENDENCIES LAYER                       │
│  Dependency Injection (Singletons, factories)           │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────┐
│                    CORE LAYER                           │
│  Settings │ Logging │ Exceptions │ Lifespan            │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────┐
│                FastAPI Application                      │
│  (app.main.py - Application Factory)                    │
└─────────────────────────────────────────────────────────┘
```

## File Structure & Responsibilities

### `app/` - FastAPI Application

**app/main.py** - Application Factory
- Role: Creates and configures the FastAPI application
- Responsibility:
  - Load settings
  - Setup logging
  - Register exception handlers
  - Configure middleware
  - Include routers
  - Manage lifespan events
- Single Responsibility: Application orchestration
- No business logic

**app/lifespan.py** - Lifecycle Management
- Role: Handles startup and shutdown events
- Responsibility:
  - Validate configuration on startup
  - Initialize logging
  - Log startup/shutdown messages
  - Placeholder for Phase 2 cleanup
- Single Responsibility: Application lifecycle

**app/__init__.py**
- Role: Package marker
- Responsibility: None

---

### `core/` - Core Application Components

**core/settings.py** - Configuration Management
- Role: Pydantic Settings class
- Responsibility:
  - Load environment variables from `.env`
  - Provide default values
  - Validate configuration structure
- Single Responsibility: Configuration
- Replaces hardcoded values

**core/logging.py** - Logging System
- Role: Structured logging configuration
- Responsibility:
  - Setup JSON or standard logging
  - Configure loggers for console output
  - Initialize root and uvicorn loggers
- Single Responsibility: Logging setup
- Used by all modules for consistent logging

**core/exceptions.py** - Custom Exceptions
- Role: Exception hierarchy
- Responsibility:
  - Define `AppException` (base)
  - Define `ValidationException` (422)
  - Define `NotFoundError` (404)
  - Define `InternalServerError` (500)
  - Define `ConfigurationError` (500)
- Single Responsibility: Exception definitions
- Used by middleware for error handling

**core/__init__.py**
- Role: Exports public API
- Responsibility: Clean imports

---

### `api/v1/` - API Endpoints (Version 1)

**api/v1/router.py** - Central Router
- Role: Aggregates all v1 endpoint routers
- Responsibility:
  - Include health endpoint router
  - Set prefix `/api/v1`
  - Organize endpoints
- Single Responsibility: Router composition

**api/v1/endpoints/health.py** - Health Check
- Role: Health check endpoint
- Responsibility:
  - Handle `GET /health`
  - Return service status, name, version
  - HTTP 200 response
- Single Responsibility: Health check
- No business logic

---

### `middleware/` - Request/Response Middleware

**middleware/cors.py** - CORS Middleware
- Role: Configure CORS settings
- Responsibility:
  - Add CORSMiddleware to FastAPI
  - Load configuration from settings
- Single Responsibility: CORS configuration

**middleware/request_id.py** - Request ID Tracking
- Role: Add unique request IDs
- Responsibility:
  - Generate or read X-Request-ID header
  - Store in request.state
  - Add to response headers
- Single Responsibility: Request identification

**middleware/timing.py** - Request Timing
- Role: Measure request duration
- Responsibility:
  - Track request processing time
  - Log timing information
  - Add X-Process-Time header
- Single Responsibility: Request timing

**middleware/error_handler.py** - Exception Handlers
- Role: Global exception handling
- Responsibility:
  - Handle AppException variants
  - Handle Pydantic ValidationError
  - Handle all unhandled exceptions
  - Return consistent error JSON
- Single Responsibility: Error handling

**middleware/__init__.py**
- Role: Exports public API
- Responsibility: Clean imports

---

### `dependencies/` - Dependency Injection

**dependencies/core.py** - Core Dependencies
- Role: Dependency injection container
- Responsibility:
  - Provide Settings singleton via `get_settings()`
  - Cache settings with `@lru_cache`
- Single Responsibility: Core dependencies

**dependencies/__init__.py**
- Role: Exports public API
- Responsibility: Clean imports

---

### `utils/` - Utility Functions

**utils/logger.py** - Logger Factory
- Role: Utility for getting loggers
- Responsibility:
  - Return configured logger for given name
- Single Responsibility: Logger creation

**utils/__init__.py**
- Role: Exports public API
- Responsibility: Clean imports

---

### Configuration Files

**.env.example** - Configuration Template
- Role: Template for environment variables
- Responsibility: Document all available settings

**.env** - Local Configuration
- Role: Development environment variables
- Responsibility: Override defaults for local development
- Should be git-ignored in production

**requirements.txt** - Dependencies
- Role: Python package dependencies
- Responsibility: List all required packages

**README.md** - Project Documentation
- Role: Setup and usage guide
- Responsibility: Instructions for installation, running, verifying

**ARCHITECTURE.md** - This File
- Role: Architecture documentation
- Responsibility: Explain design and structure

---

## Design Patterns Used

### 1. Application Factory Pattern

**File**: `app/main.py:create_app()`

```python
def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    # Configuration
    # Initialization
    # Return configured app
    return app
```

**Why**:
- Separates application creation from execution
- Enables testing with different configurations
- Allows multiple app instances if needed

### 2. Dependency Injection

**Files**: `dependencies/`, route handlers

```python
@app.get("/health")
async def health_check() -> dict[str, str]:
    settings = get_settings()
    return {...}
```

**Why**:
- Loose coupling between components
- Easy testing with mock dependencies
- Singleton pattern for expensive resources

### 3. Middleware Stack

**Files**: `middleware/*.py`

```python
app.add_middleware(TimingMiddleware)
app.add_middleware(RequestIDMiddleware)
```

**Why**:
- Separates cross-cutting concerns
- Single responsibility per middleware
- Reusable and testable

### 4. Context Manager for Lifecycle

**File**: `app/lifespan.py`

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown
```

**Why**:
- Clean separation of startup/shutdown logic
- Guaranteed cleanup on shutdown
- Native FastAPI integration

### 5. Settings Class for Configuration

**File**: `core/settings.py`

```python
class Settings(BaseSettings):
    app_name: str = "..."
    app_version: str = "..."
```

**Why**:
- Type-safe configuration
- Environment variable handling
- Default values and validation
- IDE auto-completion

### 6. Exception Hierarchy

**File**: `core/exceptions.py`

```python
class AppException(Exception):
    status_code: int
    message: str

class ValidationException(AppException):
    pass
```

**Why**:
- Consistent error handling
- Proper HTTP status codes
- Extensible for future exceptions

### 7. Structured Logging

**File**: `core/logging.py`

```python
if format_type == "json":
    formatter = jsonlogger.JsonFormatter(...)
```

**Why**:
- Machine-readable logs
- Easy parsing and aggregation
- Timestamp and context included

---

## Request Flow

```
1. HTTP Request arrives
                ↓
2. TrustedHostMiddleware (validates host)
                ↓
3. RequestIDMiddleware (adds request ID)
                ↓
4. TimingMiddleware (starts timing)
                ↓
5. CORSMiddleware (handles CORS)
                ↓
6. Route handler (endpoint)
                ↓
7. Response built
                ↓
8. TimingMiddleware (adds timing header)
                ↓
9. RequestIDMiddleware (adds request ID header)
                ↓
10. HTTP Response sent (with headers)
```

---

## Error Handling Flow

```
1. Exception occurs in route or middleware
                ↓
2. Exception bubbles up to exception handler
                ↓
3. Handler matches exception type:
   - AppException? → Use status_code & message
   - ValidationError? → Return 422 with details
   - Other Exception? → Return 500 generic error
                ↓
4. JSON response built with:
   - status (error)
   - message (error description)
   - details (if validation error)
   - request_id (for tracking)
                ↓
5. HTTP response sent
```

---

## Configuration Loading Order

```
1. Default values in Settings class
                ↓
2. Override with values from .env file
                ↓
3. Override with environment variables
                ↓
4. Final configuration used by application
```

Example:
```python
# core/settings.py
log_level: str = "INFO"  # Default

# .env
LOG_LEVEL=DEBUG          # Override from file

# Environment variable (highest priority)
export LOG_LEVEL=CRITICAL
```

---

## Testing Readiness

Phase 1 foundation enables:

### Unit Testing
- Each module has single responsibility
- Dependencies are injected
- Can mock dependencies easily

### Integration Testing
- Full app can be created with test settings
- Endpoints can be tested with test client
- Example for Phase 2:
  ```python
  from fastapi.testclient import TestClient
  from app.main import create_app
  
  app = create_app()
  client = TestClient(app)
  response = client.get("/api/v1/health")
  assert response.status_code == 200
  ```

### Configuration Testing
- Different settings via environment
- Test with production/development configs

---

## SOLID Principles Adherence

### Single Responsibility Principle
✅ Each file handles one concern
- `settings.py` → Configuration only
- `logging.py` → Logging setup only
- `health.py` → Health check only

### Open/Closed Principle
✅ Open for extension, closed for modification
- New endpoints added without modifying existing code
- New exceptions added without changing handlers
- New middleware added without changing core

### Liskov Substitution Principle
✅ Subtypes are substitutable
- All exceptions inherit from `AppException`
- All middleware implement same interface
- All dependencies return correct types

### Interface Segregation Principle
✅ Clients don't depend on interfaces they don't use
- Settings only exposes needed configuration
- Exceptions provide only necessary fields
- Middleware has minimal dependencies

### Dependency Inversion Principle
✅ Depend on abstractions, not concretions
- Route depends on `get_settings()` abstraction
- Handlers depend on exception interface
- Middleware doesn't depend on specific routes

---

## Phase 2 Preparation

Phase 1 foundation enables Phase 2 to add:

### Database Layer
- SQLAlchemy models
- Repository pattern implementation
- Database migrations

### Service Layer
- Business logic
- Service classes
- Request/response models

### Authentication
- JWT tokens
- Permission checking
- User context

### Advanced Features
- Document upload/parsing
- Embedding generation
- Vector database integration
- LangGraph agents

All without modifying Phase 1 foundation.

---

## Key Principles

1. **No Business Logic** - Phase 1 is purely infrastructure
2. **No Database** - Phase 2 will add persistence
3. **Clean Imports** - Each module exports clean API
4. **Type Safety** - Type hints on all functions
5. **Logging** - Every important action is logged
6. **Error Handling** - All errors return proper JSON
7. **Extensibility** - Easy to add new endpoints/middleware
8. **Testability** - Dependency injection enables testing

---

## Getting Started with Phase 2

To extend Phase 1:

1. Create `models/` package for SQLAlchemy models
2. Create `repositories/` package for data access
3. Create `services/` package for business logic
4. Create request/response schemas in `schemas/`
5. Update endpoints to use services
6. Add database middleware
7. Add authentication endpoints

All while keeping Phase 1 foundation unchanged.

---

## Version History

- **Phase 1.0** - Initial foundation (current)
  - FastAPI setup
  - Configuration management
  - Logging system
  - Exception handling
  - Middleware stack
  - Health endpoint
  - API versioning
