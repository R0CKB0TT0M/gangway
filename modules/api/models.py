"""
This file contains the Pydantic models for validating animation configurations.
"""

from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field

# --- Base Models ---


class RGBCCTModel(BaseModel):
    """Represents an RGBCCT color."""

    r: int = Field(0, ge=0, le=255)
    g: int = Field(0, ge=0, le=255)
    b: int = Field(0, ge=0, le=255)
    cw: int = Field(0, ge=0, le=255)
    ww: int = Field(0, ge=0, le=255)


# This will be updated later with all the specific animation models.
# AnyAnimationModel = Literal["AnyAnimationModel"]

# --- Parameter Models for each Animation ---


class AlternateParams(BaseModel):
    """Parameters for the alternate animation."""

    animations: List["AnimationModel"] = Field(default_factory=list)
    length: float = 10


class FireParams(BaseModel):
    """Parameters for the fire animation."""

    base_color: RGBCCTModel = Field(default=RGBCCTModel(r=255, g=140, b=0, cw=0, ww=0))
    flicker_speed: float = 0.1
    flicker_intensity: float = 0.5


class RainbowParams(BaseModel):
    """Parameters for the rainbow animation."""

    speed: float = 0.1
    spread: float = 3.0


class StaticParams(BaseModel):
    """Parameters for the static animation."""

    color: RGBCCTModel = Field(default=RGBCCTModel(r=255, g=255, b=255, cw=0, ww=0))


class StroboParams(BaseModel):
    """Parameters for the strobo animation."""

    colors: List[RGBCCTModel] = Field(
        default=[
            RGBCCTModel(r=255, g=255, b=255, cw=255, ww=255),
            RGBCCTModel(r=0, g=0, b=0, cw=0, ww=0),
            RGBCCTModel(r=255, g=0, b=0, cw=0, ww=0),
            RGBCCTModel(r=0, g=0, b=0, cw=0, ww=0),
            RGBCCTModel(r=0, g=0, b=255, cw=0, ww=0),
        ]
    )
    frequency: int = 100


class SwingParams(BaseModel):
    """Parameters for the swing animation."""

    color: RGBCCTModel = Field(default=RGBCCTModel(r=255, g=255, b=255, cw=255, ww=0))
    direction: Literal["x", "y"] = "y"
    wavelength: int = 50
    speed: float = 10


class Theater_chaseParams(BaseModel):
    """Parameters for the theater_chase animation."""

    color: RGBCCTModel = Field(default=RGBCCTModel(r=255, g=255, b=255, cw=0, ww=0))
    speed: float = 1.0
    spacing: int = 4


class WaveParams(BaseModel):
    """Parameters for the wave animation."""

    colors: List[RGBCCTModel] = ...
    n_waves: int = 3
    speed: float = 50.0
    wavelength: float = 200.0


class DotParams(BaseModel):
    """Parameters for the dot animation."""

    primary: Optional[Union["AnimationModel", RGBCCTModel]] = None
    secondary: Optional[Union["AnimationModel", RGBCCTModel]] = None
    radius: float = 150


class ExponentialParams(BaseModel):
    """Parameters for the exponential animation."""

    primary: Union["AnimationModel", RGBCCTModel] = Field(
        default=RGBCCTModel(r=255, g=0, b=0, cw=0, ww=0)
    )
    secondary: Union["AnimationModel", RGBCCTModel] = Field(
        default=RGBCCTModel(r=0, g=255, b=0, cw=0, ww=0)
    )
    radius: float = 150


class OffParams(BaseModel):
    """Parameters for the off animation."""

    pass


class IdleParams(BaseModel):
    """Parameters for the idle animation."""

    idle_animation: Union["AnimationModel", RGBCCTModel] = Field(
        default=RGBCCTModel(r=255, g=0, b=0, cw=0, ww=0)
    )
    active_animation: Union["AnimationModel", RGBCCTModel] = Field(
        default=RGBCCTModel(r=0, g=255, b=0, cw=0, ww=0)
    )

    class Config:
        extra = "forbid"  # Disallow other keys


# --- Animation Wrapper Models (to enforce {'name': params} structure) ---


class AlternateAnimation(BaseModel):
    """Wrapper for the alternate animation."""

    alternate: AlternateParams = Field(...)

    class Config:
        extra = "forbid"  # Disallow other keys


class FireAnimation(BaseModel):
    """Wrapper for the fire animation."""

    fire: FireParams = Field(...)

    class Config:
        extra = "forbid"  # Disallow other keys


class RainbowAnimation(BaseModel):
    """Wrapper for the rainbow animation."""

    rainbow: RainbowParams = Field(...)

    class Config:
        extra = "forbid"  # Disallow other keys


class StaticAnimation(BaseModel):
    """Wrapper for the static animation."""

    static: StaticParams = Field(...)

    class Config:
        extra = "forbid"  # Disallow other keys


class StroboAnimation(BaseModel):
    """Wrapper for the strobo animation."""

    strobo: StroboParams = Field(...)

    class Config:
        extra = "forbid"  # Disallow other keys


class SwingAnimation(BaseModel):
    """Wrapper for the swing animation."""

    swing: SwingParams = Field(...)

    class Config:
        extra = "forbid"  # Disallow other keys


class Theater_chaseAnimation(BaseModel):
    """Wrapper for the theater_chase animation."""

    theater_chase: Theater_chaseParams = Field(...)

    class Config:
        extra = "forbid"  # Disallow other keys


class WaveAnimation(BaseModel):
    """Wrapper for the wave animation."""

    wave: WaveParams = Field(...)

    class Config:
        extra = "forbid"  # Disallow other keys


class DotAnimation(BaseModel):
    """Wrapper for the dot animation."""

    dot: DotParams = Field(...)

    class Config:
        extra = "forbid"  # Disallow other keys


class ExponentialAnimation(BaseModel):
    """Wrapper for the exponential animation."""

    exponential: ExponentialParams = Field(...)

    class Config:
        extra = "forbid"  # Disallow other keys


class OffAnimation(BaseModel):
    """Wrapper for the off animation."""

    off: OffParams = Field(...)

    class Config:
        extra = "forbid"  # Disallow other keys


class IdleAnimation(BaseModel):
    """Wrapper for the idle animation."""

    idle: IdleParams = Field(...)

    class Config:
        extra = "forbid"  # Disallow other keys


# --- Union of All Animation Models ---
AnimationModel = Union[
    AlternateAnimation,
    FireAnimation,
    RainbowAnimation,
    StaticAnimation,
    StroboAnimation,
    SwingAnimation,
    Theater_chaseAnimation,
    WaveAnimation,
    DotAnimation,
    ExponentialAnimation,
    OffAnimation,
    IdleAnimation,
]

# --- Rebuild Models to Resolve Forward References ---
AlternateParams.model_rebuild()
FireParams.model_rebuild()
RainbowParams.model_rebuild()
StaticParams.model_rebuild()
StroboParams.model_rebuild()
SwingParams.model_rebuild()
Theater_chaseParams.model_rebuild()
WaveParams.model_rebuild()
DotParams.model_rebuild()
ExponentialParams.model_rebuild()
OffParams.model_rebuild()
IdleParams.model_rebuild()
