from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import Base, async_engine
from fastapi.concurrency import asynccontextmanager
from dotenv import load_dotenv
from app.routers import user, inbound, outbound, inventory, product, location
load_dotenv(dotenv_path=".env")

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
    allow_origins=["http://localhost:3000"],
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