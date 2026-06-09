from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import generate

app = FastAPI(title="AutoCHAD Engine API", version="1.0.0")

# Allow requests from the local Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generate.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "AutoCHAD CAD generation engine is running."}
