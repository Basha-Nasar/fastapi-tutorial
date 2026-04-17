from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routes.users import router as users_router
from app.middleware.timer import timer_middleware
from fastapi.middleware.cors import CORSMiddleware
from app.database import AsyncSessionLocal, engine, create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield


app = FastAPI(lifespan=lifespan)


app.middleware('http')(timer_middleware)
app.include_router(users_router)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session




app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)