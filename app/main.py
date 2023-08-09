"""
메인
"""
import os

from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware
from mangum import Mangum
from server_modules.database import SQLALCHEMY_DATABASE_URL
from server_modules.startup import apply_custom_openapi, apply_catch_internal_error, apply_alembic_startup, \
    apply_include_routers
from server_modules.user_auth_router import get_user_auth_router
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware

STAGE = os.getenv('STAGE', 'local')
app = FastAPI(title="데브파이브", description="데브파이브 서버 시스템",
              docs_url=None if STAGE == 'prod' else '/docs',
              openapi_url=None if STAGE == 'prod' else '/openapi.json',
              redoc_url=None if STAGE == 'prod' else '/redoc')

# DB 연동 설정
apply_alembic_startup(app)
app.add_middleware(DBSessionMiddleware,
                   db_url=SQLALCHEMY_DATABASE_URL)
# ###################


apply_catch_internal_error(app)
apply_custom_openapi(app, STAGE)

app.add_middleware(GZipMiddleware, minimum_size=1000)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if STAGE != "prod" else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

apply_include_routers(app)
app.include_router(get_user_auth_router())


@app.get("/")
async def root():
    """
    root
    """
    return "Devfive api server"


handler = Mangum(app)
