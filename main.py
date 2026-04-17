from fastapi import FastAPI
from app.routes.users import router as users_router
from app.middleware.timer import timer_middleware
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.middleware('http')(timer_middleware)
app.include_router(users_router)

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)