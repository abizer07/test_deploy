from fastapi import FastAPI
from app.routes import router
from tally_integration.routes import router as tally_router

app = FastAPI(title="Auto Accountant API")
app.include_router(router)
app.include_router(tally_router)


@app.get("/health")
async def health():
    return {"status": "ok"}