from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.domains.auth.router import router as auth_router
from src.domains.reservations.router import router as reservations_router
from src.domains.resources.router import router as resources_router
from src.domains.users.router import router as users_router
from src.models import *  # noqa: F401, F403, RUF100
import resend
from src.config import settings

app = FastAPI()
app.include_router(resources_router)
app.include_router(auth_router)
app.include_router(reservations_router)
app.include_router(users_router)

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "Content-Range"],
)

resend.api_key = settings.RESEND_API_KEY.get_secret_value()


@app.post("/send-email")
async def send_email():
    payload = {
        "from": "noreply@dreambyte.es",
        "subject": "Test Email",
        "html": "<strong>Hola manco:V!</strong>",
    }
    try:
        return resend.Emails.send(payload)
    except Exception as e:
        return {"message": "Failed to send email", "error": str(e)}
