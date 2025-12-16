from fastapi import FastAPI
from fastapi_app.api.email import router as email_router

app = FastAPI(title="Email Integration Service")

app.include_router(email_router)
