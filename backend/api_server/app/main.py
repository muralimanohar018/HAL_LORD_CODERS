from fastapi import FastAPI

from app.api.analyze import router as analyze_router
from app.api.history import router as history_router

app = FastAPI(title="Risk Analysis API", version="1.0.0")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(analyze_router)
app.include_router(history_router)
