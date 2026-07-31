import asyncio
from fastapi import FastAPI
from src.database import engine, Base
from contextlib import asynccontextmanager
from src.domains.resources.router import router as resources_router


app = FastAPI()
app.include_router(resources_router)