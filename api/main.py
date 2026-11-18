"""FastAPI version of the exposure API.

Run it with:  uvicorn api.main:app --reload
Docs:         http://127.0.0.1:8000/docs
"""
from typing import Annotated

from fastapi import FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from api.serializers import ErrorResponse, ExposureRequest, ExposureResponse
from calculator.service import calculate

app = FastAPI(title="Exposure Calculator API")


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    """Return 400 with Django-style errors instead of FastAPI's default 422."""
    errors: dict[str, list[str]] = {}
    for err in exc.errors():
        loc = [str(part) for part in err["loc"] if part not in ("query", "body")]
        field = loc[0] if loc else "__all__"        # model-level check -> "__all__", like Django
        message = err["msg"].removeprefix("Value error, ")
        errors.setdefault(field, []).append(message)
    return JSONResponse({"errors": errors}, status_code=400)


ERRORS = {400: {"model": ErrorResponse}}


@app.get("/api/exposure/", response_model=ExposureResponse, responses=ERRORS)
def exposure_get(params: Annotated[ExposureRequest, Query()]):
    """Same query string as the Django API: ?light=12&aperture=5.6&iso=200"""
    return calculate(params.to_calc_input())


@app.post("/api/exposure/", response_model=ExposureResponse, responses=ERRORS)
def exposure_post(body: ExposureRequest):
    """JSON body: {"light": 12, "aperture": 5.6, "iso": 200}"""
    return calculate(body.to_calc_input())
