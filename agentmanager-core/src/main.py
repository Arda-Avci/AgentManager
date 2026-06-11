from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router
from src.auth.middleware import APIKeyMiddleware
from src.config import settings
from src.mcp_server import mcp_server, setup_mcp
from src.providers.registry import ProviderRegistry
from src.router import LLMRouter
from src.ws_manager import ws_manager

router_ = LLMRouter()
provider_registry = ProviderRegistry()


@asynccontextmanager
async def lifespan(app: FastAPI):
    from src.database.engine import init_db
    await init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)

app.state.auth_enabled = not settings.debug

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(APIKeyMiddleware)

if not settings.debug:
    from src.api.middleware import RateLimitMiddleware
    app.add_middleware(RateLimitMiddleware)

app.include_router(router)

setup_mcp(router_)
app.mount("/mcp", mcp_server.sse_app())

app.state.llm_router = router_
app.state.provider_registry = provider_registry
app.state.ws_manager = ws_manager
