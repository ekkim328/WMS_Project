from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.db.database import Base, async_engine
from fastapi.concurrency import asynccontextmanager
from dotenv import load_dotenv
from app.routers import user, inbound, outbound, inventory, product, location, history
load_dotenv(dotenv_path=".env")

from app.routers.admin_seed import router as admin_seed_router

# 애플리케이션의 시작과 종료 시 실행될 작업을 정의함
# 시작/끝을 비동기적으로 처리
@asynccontextmanager
async def lifespan(app:FastAPI):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await async_engine.dispose()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# 라우터 만든거 추가해주기
app.include_router(user.router)
app.include_router(inbound.router)
app.include_router(outbound.router)
app.include_router(inventory.router)
app.include_router(product.router)
app.include_router(location.router)
app.include_router(history.router)
app.include_router(admin_seed_router)


@app.get("/healthz", include_in_schema=False)
async def healthz():
    return {"status": "ok"}


ROOT_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIST = ROOT_DIR / "frontend" / "dist"

if FRONTEND_DIST.exists():
    app.mount(
        "/assets",
        StaticFiles(directory=FRONTEND_DIST / "assets"),
        name="frontend-assets",
    )


    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend(full_path: str):
        index_path = FRONTEND_DIST / "index.html"
        if not index_path.exists():
            raise HTTPException(status_code=404, detail="Frontend build not found")
        return FileResponse(index_path)
