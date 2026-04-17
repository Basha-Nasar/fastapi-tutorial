# Async SQLAlchemy with psycopg3 Design

**Date:** 2026-04-17
**Objective:** Migrate database layer from synchronous SQLAlchemy to async SQLAlchemy 2.0+ with psycopg3 driver for non-blocking database operations in FastAPI.

## Context

Current state:
- FastAPI application with SQLAlchemy ORM using synchronous `create_engine`
- PostgreSQL connection via psycopg2 (not yet installed, causing import error)
- FastAPI routes are set up but database operations are synchronous
- Synchronous DB calls block the event loop

## Solution Overview

Migrate to async-first database layer:
- Replace `create_engine` with `create_async_engine`
- Replace `SessionLocal` with `AsyncSession` from `sqlalchemy.ext.asyncio`
- Convert connection string dialect to `postgresql+psycopg://`
- Update `get_db()` dependency to async generator
- Ensure all routes using database are `async def`

This provides:
- Non-blocking database I/O
- Better scalability under load
- Compatibility with async FastAPI patterns

## Dependencies

### New/Updated Packages
- `sqlalchemy[asyncio]` — async support for SQLAlchemy (likely already installed, just ensure async extra is present)
- `psycopg[binary]` — psycopg3 driver with pre-built bindings for easier installation

No removal of existing packages; these are additive.

## Architecture

### Database Module (app/database.py)

```
create_async_engine(DATABASE_URL)
    ↓
async_sessionmaker (bound to engine)
    ↓
AsyncSession instances
```

Key changes:
- `create_engine()` → `create_async_engine()`
- `sessionmaker` → `async_sessionmaker` (from `sqlalchemy.ext.asyncio`)
- Connection string: `postgresql+psycopg://postgress:123456@localhost:5432/fastapi_tutorial`
- Session configuration remains: `autocommit=False, autoflush=False`

### Dependency Injection (main.py)

```python
async def get_db():
    async with AsyncSession(engine) as session:
        yield session
```

- Changed from sync generator to async generator
- Uses async context manager for proper cleanup
- All errors during session usage are caught and session is closed

### Route Integration

Any route that accepts `db: AsyncSession = Depends(get_db)`:
- Must be declared `async def`
- All database queries must use `await`
- Example: `await db.execute(select(User))` instead of `db.execute(select(User))`

## Data Flow

```
HTTP Request
  ↓
FastAPI route (async)
  ↓
Dependency: get_db() yields AsyncSession
  ↓
SQLAlchemy query with await
  ↓
psycopg3 async driver
  ↓
PostgreSQL
  ↓
Response (async)
```

## Error Handling

- Async context manager in `get_db()` ensures session cleanup on exceptions
- Connection pool managed by `create_async_engine` handles reconnects
- SQLAlchemy exception handling remains unchanged

## Testing Implications

- Any test using the database must be async
- Test fixtures should use `AsyncSession` with test database URL
- Can use `pytest-asyncio` for async test support

## Scope

### Included
- Update [app/database.py](app/database.py) to use async engine and sessions
- Update [main.py](main.py) `get_db()` dependency to async
- Install psycopg3 and sqlalchemy[asyncio]
- Convert existing routes to async (if not already)

### Not Included
- Refactoring existing models or queries
- Test suite setup (separate concern)
- Connection pool tuning (can be added later if needed)

## Implementation Order

1. Install dependencies
2. Update [app/database.py](app/database.py)
3. Update [main.py](main.py) get_db()
4. Convert routes to async def (if needed)
5. Test connection works

## Success Criteria

- `psycopg3` driver loads without import errors
- Database connection established via async engine
- GET/POST requests to routes complete without blocking
- Sessions properly close after each request
