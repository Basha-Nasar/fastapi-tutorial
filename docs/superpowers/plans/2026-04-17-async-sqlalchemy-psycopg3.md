# Async SQLAlchemy with psycopg3 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate database layer from synchronous SQLAlchemy to async SQLAlchemy with psycopg3 for non-blocking database I/O.

**Architecture:** Replace `create_engine` with `create_async_engine`, update `SessionLocal` to `AsyncSession`, convert `get_db()` to async generator, ensure all DB-using routes are `async def`.

**Tech Stack:** FastAPI, SQLAlchemy 2.0+, psycopg3, asyncio

---

## Task 1: Install Dependencies

**Files:**
- Modify: `requirements.txt` (or equivalent dependency file)

- [ ] **Step 1: Check current dependency file format**

Run: `ls -la c:\dev\sites\fastapi-tutorial | grep -E "(requirements|pyproject|poetry|pipfile)"`

Expected: Shows which file is used for dependencies (likely requirements.txt)

- [ ] **Step 2: Update dependencies**

If using **requirements.txt**, add/ensure these lines exist:
```
sqlalchemy[asyncio]>=2.0.0
psycopg[binary]>=3.0.0
```

If using **pyproject.toml**, add to dependencies section:
```toml
sqlalchemy = { version = ">=2.0.0", extras = ["asyncio"] }
psycopg = { version = ">=3.0.0", extras = ["binary"] }
```

- [ ] **Step 3: Install dependencies**

Run: `pip install -r requirements.txt` (or `pip install -e .` for pyproject.toml)

Expected: Installs psycopg3 and async SQLAlchemy without errors

- [ ] **Step 4: Verify installation**

Run: `python -c "import psycopg; import sqlalchemy; print('OK')"`

Expected: Output `OK` with no ImportError

- [ ] **Step 5: Commit**

```bash
git add requirements.txt
git commit -m "deps: add psycopg3 and sqlalchemy[asyncio]"
```

---

## Task 2: Update Database Configuration

**Files:**
- Modify: `app/database.py`

- [ ] **Step 1: Read current database.py**

Run: `cat app/database.py`

Confirm it has:
- `create_engine` call
- `sessionmaker` usage
- PostgreSQL connection string

- [ ] **Step 2: Write new async database.py**

Replace entire file with:

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

DATABASE_URL = "postgresql+psycopg://postgress:123456@localhost:5432/fastapi_tutorial"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL debugging
    pool_size=20,
    max_overflow=0,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()
```

Key changes:
- `create_engine` → `create_async_engine` (async driver support)
- `postgresql://` → `postgresql+psycopg://` (psycopg dialect)
- `sessionmaker` → `async_sessionmaker` (from sqlalchemy.ext.asyncio)
- `SessionLocal` → `AsyncSessionLocal` (naming convention for async)
- Added `Base` for model declarations (needed for async context)

- [ ] **Step 3: Verify file syntax**

Run: `python -m py_compile app/database.py`

Expected: No output (compilation successful)

- [ ] **Step 4: Commit**

```bash
git add app/database.py
git commit -m "refactor: convert database to async SQLAlchemy with psycopg3"
```

---

## Task 3: Update FastAPI Dependency

**Files:**
- Modify: `main.py` (specifically the `get_db()` function and imports)

- [ ] **Step 1: Read current main.py**

Run: `cat main.py`

Confirm it imports `SessionLocal` from `app.database` and has a `get_db()` function

- [ ] **Step 2: Update imports**

Replace this line:
```python
from app.database import SessionLocal, engine
```

With:
```python
from app.database import AsyncSessionLocal, engine
```

- [ ] **Step 3: Replace get_db() function**

Find and replace the current `get_db()` function:

Old:
```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

get_db()
```

New:
```python
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

Key changes:
- `def` → `async def` (async generator)
- `SessionLocal()` → `AsyncSessionLocal()` (async session factory)
- `try/finally` → `async with` (async context manager handles cleanup)
- Removed `get_db()` call at module level (not needed)

- [ ] **Step 4: Verify file syntax**

Run: `python -m py_compile main.py`

Expected: No output (compilation successful)

- [ ] **Step 5: Verify FastAPI can load**

Run: `python -c "from main import app; print('OK')"`

Expected: Output `OK` (no import errors)

- [ ] **Step 6: Commit**

```bash
git add main.py
git commit -m "refactor: convert get_db() dependency to async"
```

---

## Task 4: Check and Update Routes

**Files:**
- Modify: `app/routes/users.py` (or any file using the db dependency)

- [ ] **Step 1: Examine users router**

Run: `cat app/routes/users.py`

Look for function definitions that have `db: SessionLocal = Depends(get_db)` parameter

- [ ] **Step 2: Check if routes are async**

Confirm all route handlers using the `db` parameter have `async def` (not `def`):

Expected pattern:
```python
@router.get("/users")
async def list_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()
```

If any routes are `def` instead of `async def`, update them to `async def`.

- [ ] **Step 3: Update query execution**

Ensure all SQLAlchemy queries use `await`:
- `db.execute(...)` → `await db.execute(...)`
- `db.query(...)` → `await db.execute(select(...))`  (if using .query() style)

If file uses `.query()` style (legacy), convert to `select()` style (modern async-friendly):

Old:
```python
db.query(User).filter(User.id == user_id).first()
```

New:
```python
stmt = select(User).where(User.id == user_id)
result = await db.execute(stmt)
return result.scalar_one_or_none()
```

- [ ] **Step 4: Run type check**

Run: `python -m py_compile app/routes/users.py`

Expected: No output (syntax OK)

- [ ] **Step 5: Commit if changes made**

```bash
git add app/routes/users.py
git commit -m "refactor: convert user routes to async queries"
```

If no changes were needed, skip this step.

---

## Task 5: Test Database Connection

**Files:**
- No files created/modified (testing existing setup)

- [ ] **Step 1: Create simple test script**

Create `test_connection.py` at project root:

```python
import asyncio
from app.database import engine, AsyncSessionLocal
from sqlalchemy import text

async def test_connection():
    """Test async database connection"""
    try:
        # Test engine connection
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("✓ Engine connection successful")

        # Test AsyncSession
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            print("✓ AsyncSession connection successful")

        print("\n✓ All database connections working!")
        return True
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False
    finally:
        await engine.dispose()

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    exit(0 if success else 1)
```

- [ ] **Step 2: Run the test**

Run: `python test_connection.py`

Expected output:
```
✓ Engine connection successful
✓ AsyncSession connection successful

✓ All database connections working!
```

If you see connection errors:
- Verify PostgreSQL is running: `psql -U postgress -d fastapi_tutorial -c "SELECT 1"`
- Check credentials in `app/database.py` match your PostgreSQL setup
- Ensure database `fastapi_tutorial` exists

- [ ] **Step 3: Delete test script**

Run: `rm test_connection.py`

(Test was for verification only, not part of codebase)

- [ ] **Step 4: Test FastAPI startup**

Run: `uvicorn main:app --reload`

Expected: Server starts without "No module named 'psycopg2'" error

Stop the server: `Ctrl+C`

- [ ] **Step 5: Verify no outstanding changes**

Run: `git status`

Expected: Only modified files should be `main.py`, `app/database.py`, `app/routes/users.py` (if it had routes), and `requirements.txt`

If you have untracked files or uncommitted changes, decide whether they're part of this task. Typically: no.

---

## Verification Checklist

Before considering this complete:

- [ ] `pip list | grep psycopg` shows `psycopg >=3.0.0` installed
- [ ] `app/database.py` uses `create_async_engine` and `AsyncSessionLocal`
- [ ] `main.py` imports `AsyncSessionLocal` and `get_db()` is `async def`
- [ ] All route handlers using `db` are `async def`
- [ ] All database queries use `await db.execute(...)`
- [ ] `python test_connection.py` passes (before deletion)
- [ ] `uvicorn main:app` starts without "No module named 'psycopg'" errors
- [ ] Git log shows commits for: deps, database refactor, and routes refactor (if needed)

---

## Common Issues & Solutions

**Issue:** `ModuleNotFoundError: No module named 'psycopg'`
- **Solution:** Ran `pip install -r requirements.txt` but psycopg didn't install. Check pip output for errors. May need `pip install --upgrade pip` first.

**Issue:** `sqlalchemy.exc.NoSuchModuleError: Can't load plugin: sqlalchemy.dialects:postgresql.psycopg`
- **Solution:** Make sure connection string uses `postgresql+psycopg://` (not `postgresql://`)

**Issue:** `TypeError: object AsyncSession can't be used in 'await' expression`
- **Solution:** Routes are using `AsyncSession` correctly, but a query isn't awaited. Ensure all `db.execute()` calls have `await` in front.

**Issue:** `RuntimeError: Event loop is closed`
- **Solution:** Don't call `get_db()` at module level (Task 3 removes the `get_db()` call that was there). It should only be called via FastAPI's dependency injection.
