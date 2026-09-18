from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.routers.suppliers import router as suppliers_router
from app.core.config import get_settings
from app.core.rate_limit import limiter
from app.db.session import Base, engine
from app.seed import seed_if_empty

settings = get_settings()

app = FastAPI(title="Supplier Catalog API")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(suppliers_router)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    seed_if_empty()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
