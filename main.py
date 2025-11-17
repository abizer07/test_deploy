from fastapi import FastAPI
from app.routes import router
from tally_integration.routes import router as tally_router
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="Auto Accountant API")
app.include_router(router)
app.include_router(tally_router)

# Serve static frontend folder
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def root():
    return FileResponse("frontend/index.html")
@app.get("/health")
async def health():
    return {"status": "ok"}