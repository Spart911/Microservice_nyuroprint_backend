from fastapi import FastAPI

from src.Config.db import engine, Base
from src.Routers.v1.user_router import router as user_router
from src.Helpers.MiddlewareHelper import MiddlewareHelper

app = FastAPI()


MiddlewareHelper.setCors(app)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.include_router(user_router)