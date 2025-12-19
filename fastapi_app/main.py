import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi_app.api.email import router as email_router


app = FastAPI(title="Email Integration Service")

# ========================
# CORS Configuration
# ========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # Local development
        "http://localhost:8000",      # FastAPI docs
        "http://127.0.0.1:3000",      # Local (127.0.0.1)
        "http://127.0.0.1:8000",      # FastAPI docs (127.0.0.1)
        "file://",                    # File protocol (HTML opened directly)
    ],
    allow_credentials=True,
    allow_methods=["*"],              # Allow all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],              # Allow all headers
)

app.include_router(email_router)
