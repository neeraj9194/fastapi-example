from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
import time

from fastapi import Request

from apps.basic_example.api import router as user_router
from core.db import DB_CONFIG

app = FastAPI(title="FASTAPI")
app.include_router(user_router, prefix="/api")


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


register_tortoise(
    app,
    config=DB_CONFIG,
    generate_schemas=True,
    add_exception_handlers=True,
)
