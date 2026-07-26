"""FastAPI application entry point for ProducerGPT."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.api.routes import get_openai_service, router
from backend.core.config import get_settings


FRONTEND_DIRECTORY = Path(__file__).resolve().parents[1] / "frontend"


def configure_logging(log_level: str) -> None:
    """Configure concise process-wide logging for API and agent observability."""

    logging.basicConfig(
        level=log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Initialize logging and release the cached OpenAI client on shutdown."""

    settings = get_settings()
    configure_logging(settings.log_level)
    logging.getLogger(__name__).info("Starting %s", settings.app_name)
    yield

    if get_openai_service.cache_info().currsize:
        await get_openai_service().close()
    logging.getLogger(__name__).info("Stopped %s", settings.app_name)


def create_app() -> FastAPI:
    """Build and configure the ProducerGPT ASGI application."""

    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="An Autonomous Hollywood Studio powered by AI Agents.",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url=None,
    )
    application.include_router(router)
    application.mount(
        "/demo",
        StaticFiles(directory=FRONTEND_DIRECTORY, html=True),
        name="demo",
    )
    return application


app = create_app()


if __name__ == "__main__":
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)