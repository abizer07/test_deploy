import os
import asyncio
from fastapi import FastAPI
from app.routes import router
from tally_integration.routes import router as tally_router
from invoices_api.routes import invoices_api_router
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from invoices_api.models import Invoice


app = FastAPI(title="Auto Accountant API")

app.include_router(router)
app.include_router(tally_router)
app.include_router(invoices_api_router)


app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.on_event("startup")
async def init_db():
    mongo_url = os.getenv("MONGO_URL")  # ✅ READS FROM docker-compose

    if not mongo_url:
        raise RuntimeError("MONGO_URL not set in environment")

    # ✅ Retry logic so app doesn't crash if Mongo starts slowly
    for attempt in range(10):
        try:
            client = AsyncIOMotorClient(mongo_url)
            await init_beanie(
                database=client.get_default_database(),
                document_models=[Invoice]
            )
            print("✅ MongoDB connected successfully")
            return
        except Exception as e:
            print(f"❌ Mongo not ready (attempt {attempt+1}/10): {e}")
            await asyncio.sleep(3)

    raise RuntimeError("❌ Could not connect to MongoDB after multiple retries")


@app.get("/")
async def root():
    return FileResponse("frontend/index.html")


@app.get("/health")
async def health():
    return {"status": "ok"}
