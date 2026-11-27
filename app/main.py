import os
import secrets

from fastapi import Depends, FastAPI, HTTPException, Request, Security
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader

from app import model
from app.schemas import Application, Health, Prediction

app = FastAPI(
    title="BAF Fraud Detection API",
    description="Skor peluang penipuan untuk pengajuan buka rekening (LightGBM, data BAF). "
    "Kirim header `x-api-key`.",
)

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)


@app.exception_handler(RequestValidationError)
def validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
    # buang "input": NaN yang ditolak tidak bisa di-encode ke JSON dan membuat 422 bawaan crash
    errors = [{k: v for k, v in e.items() if k != "input"} for e in exc.errors()]
    return JSONResponse(status_code=422, content={"detail": jsonable_encoder(errors)})


def require_api_key(key: str | None = Security(api_key_header)) -> None:
    expected = os.environ.get("API_KEY")  # dibaca per request; tanpa env, tidak ada kunci yang lolos
    if not expected:
        raise HTTPException(500, "API key belum dikonfigurasi di server")
    if key is None or not secrets.compare_digest(key.encode(), expected.encode()):
        raise HTTPException(401, "x-api-key tidak valid")


@app.get("/health", response_model=Health)
@app.api_route("/health", methods=["HEAD"], include_in_schema=False)  # uptime monitor sering pakai HEAD
@app.api_route("/", methods=["GET", "HEAD"], response_model=Health, include_in_schema=False)
def health() -> dict:
    """Status layanan dan versi model yang sedang dimuat (tanpa x-api-key)."""
    return {"status": "ok", "model_name": model.MODEL_NAME, "model_version": model.MODEL_VERSION}


@app.post("/predict", response_model=Prediction, dependencies=[Depends(require_api_key)])
def predict(body: Application) -> dict:
    return model.predict(body.model_dump())
