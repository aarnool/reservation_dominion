import asyncio
from fastapi import FastAPI
from src.database import engine, Base
from contextlib import asynccontextmanager


app = FastAPI()