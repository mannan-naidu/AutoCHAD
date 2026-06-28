import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import generate

if not os.getenv("GROQ_API_KEY"):
    print("FATAL: GROQ_API_KEY environment variable is not set.", file=sys.stderr)
    sys.exit(1)

app = FastAPI(title="AutoCHAD Engine API", version="1.0.0")

_raw_origins = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = [o.strip() for o in _raw_origins.split(",")] if _raw_origins != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generate.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "AutoCHAD CAD generation engine is running."}
