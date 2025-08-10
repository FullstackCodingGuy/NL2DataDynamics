from fastapi import FastAPI
from .routes import router

app = FastAPI(
    title="Agentic Analytics Tool",
    description="Backend API for analytics, database integration, plugins, and authentication.",
    version="0.1.0"
)

app.include_router(router)

@app.get("/health")
def health_check():
    return {"status": "ok"}