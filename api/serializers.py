"""Pydantic models for the FastAPI app: the FastAPI version of DRF serializers.

ExposureRequest checks the input the same way calculator.forms.ExposureForm does,
and ExposureResponse describes the JSON that calculate() returns.
"""
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from calculator.core import parse_shutter
from calculator.scenes import SCENES
from calculator.stops import APERTURES, ISOS, SHUTTERS

LIGHT_VALUES = {ev for ev, _ in SCENES}


class ExposureRequest(BaseModel):
    """Light plus exactly two settings; the empty one gets calculated."""

    light: int = Field(description="Scene brightness as EV100, from calculator.scenes", examples=[12])
    aperture: float | None = Field(None, description="f-number, e.g. 5.6", examples=[5.6])
    shutter: str | None = Field(None, description='"1/250" or "2" (seconds)', examples=["1/250"])
    iso: int | None = Field(None, examples=[200])

    # An HTML form sends "aperture=" for "— calculate —": treat it as missing.
    @field_validator("aperture", "shutter", "iso", mode="before")
    @classmethod
    def empty_is_none(cls, value):
        return None if value == "" else value

    @field_validator("light")
    @classmethod
    def known_light(cls, value):
        if value not in LIGHT_VALUES:
            raise ValueError(f"Choose one of: {sorted(LIGHT_VALUES)}")
        return value

    @field_validator("aperture")
    @classmethod
    def real_aperture(cls, value):
        if value is not None and value not in APERTURES:
            raise ValueError("Not a standard aperture (f/1.0 ... f/32 in 1/3 stops)")
        return value

    @field_validator("shutter")
    @classmethod
    def real_shutter(cls, value):
        if value is not None and value not in SHUTTERS:
            raise ValueError('Not a standard shutter speed, use a value like "1/125" or "2"')
        return value

    @field_validator("iso")
    @classmethod
    def real_iso(cls, value):
        if value is not None and value not in ISOS:
            raise ValueError("Not a standard ISO (50 ... 25600 in 1/3 stops)")
        return value

    @model_validator(mode="after")
    def exactly_one_missing(self):
        if [self.aperture, self.shutter, self.iso].count(None) != 1:
            raise ValueError("Fill in two settings and leave one empty: that one gets calculated.")
        return self

    def to_calc_input(self) -> dict:
        """The dict calculate() expects, with the shutter in seconds."""
        return {
            "light": self.light,
            "aperture": self.aperture,
            "shutter": parse_shutter(self.shutter) if self.shutter else None,
            "iso": self.iso,
        }


class Settings(BaseModel):
    aperture: float
    shutter: str = Field(description='Formatted, e.g. "1/250" or "0.8s"')
    iso: int


class ExposureResponse(BaseModel):
    ev100: int
    solved: Literal["aperture", "shutter", "iso"]
    exact: Settings = Field(description="The calculated value before rounding")
    camera: Settings = Field(description="Rounded to the nearest real camera setting")
    stops_off: float = Field(description="+ means brighter than the meter wants")
    out_of_range: bool = Field(description="Rounding moved it more than half a stop")


class ErrorResponse(BaseModel):
    """Same shape as the Django API: {"errors": {"field": ["message"]}}."""

    errors: dict[str, list[str]]
