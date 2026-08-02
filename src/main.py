import asyncio
from fastapi import FastAPI
from src.database import engine, Base
from contextlib import asynccontextmanager
from src.domains.resources.router import router as resources_router
from src.domains.auth.router import router as auth_router


app = FastAPI()
app.include_router(resources_router)
app.include_router(auth_router)