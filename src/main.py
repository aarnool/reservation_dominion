from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.domains.resources.router import router as resources_router
from src.domains.auth.router import router as auth_router
from src.domains.reservations.router import router as reservations_router
from src.domains.users.router import router as users_router

app = FastAPI   ()
app.include_router(resources_router)
app.include_router(auth_router)
app.include_router(reservations_router)
app.include_router(users_router)

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "Content-Range"]
)