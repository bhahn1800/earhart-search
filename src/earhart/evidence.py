"""Evidence registry schema.

Observed evidence and inferred values are separate record kinds. A record never
carries a model constant; model parameters cite evidence ids instead.
"""

from __future__ import annotations

import json
from datetime import datetime
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field, field_validator, model_validator


class SourceType(StrEnum):
    PRIMARY = "PRIMARY"
    CONTEMPORARY_SECONDARY = "CONTEMPORARY_SECONDARY"
    MODERN_ANALYSIS = "MODERN_ANALYSIS"
    SPECULATIVE = "SPECULATIVE"


class TimeSystem(StrEnum):
    """Clock in which date_time is expressed. Mixing these is a classic 1937 error source."""

    GCT = "GCT"  # Greenwich civil time, as used in Itasca / Earhart radio logs
    ZONE_LAE = "ZONE_LAE"  # Lae local (zone to be verified)
    ZONE_ITASCA = "ZONE_ITASCA"  # Itasca ship's time (zone to be verified)
    HOWLAND_LOCAL = "HOWLAND_LOCAL"
    UTC = "UTC"
    UNKNOWN = "UNKNOWN"


class Category(StrEnum):
    DEPARTURE = "DEPARTURE"
    RADIO_TRANSMISSION = "RADIO_TRANSMISSION"
    RADIO_RECEPTION_LOG = "RADIO_RECEPTION_LOG"
    FUEL = "FUEL"
    AIRCRAFT_PERFORMANCE = "AIRCRAFT_PERFORMANCE"
    NAVIGATION = "NAVIGATION"
    WEATHER = "WEATHER"
    SHIP_POSITION = "SHIP_POSITION"
    SEARCH_TRACK = "SEARCH_TRACK"
    GEOGRAPHY = "GEOGRAPHY"
    MODERN_SEARCH = "MODERN_SEARCH"
    OTHER = "OTHER"


class Uncertainty(BaseModel):
    """Positional/temporal uncertainty of the *record*, free of model assumptions."""

    horizontal_nm: float | None = Field(None, ge=0)
    time_seconds: float | None = Field(None, ge=0)
    description: str = ""


class EvidenceRecord(BaseModel):
    id: str = Field(pattern=r"^[A-Z]{2,6}-\d{3,}$")
    date_time: datetime | None = None
    time_system: TimeSystem = TimeSystem.UNKNOWN
    category: Category
    observation: str = Field(min_length=1, description="What the source reports, paraphrase allowed")
    original_text: str | None = Field(None, description="Verbatim quote; required for PRIMARY sources")
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    uncertainty: Uncertainty = Field(default_factory=Uncertainty)
    source_title: str
    source_url: str | None = None
    source_type: SourceType
    source_quality: int = Field(ge=1, le=5, description="1 = unreliable ... 5 = verified original document")
    interpretation: str = Field("", description="Inferred meaning. Kept apart from `observation`.")
    notes: str = ""
    verified: bool = Field(False, description="True only after a human compared against the cited source")

    @model_validator(mode="after")
    def _checks(self):
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("latitude and longitude must be given together")
        if self.source_type is SourceType.PRIMARY and not self.original_text:
            raise ValueError("PRIMARY records require original_text")
        if self.source_type is SourceType.SPECULATIVE and self.source_quality > 2:
            raise ValueError("SPECULATIVE sources cannot have source_quality > 2")
        if self.latitude is not None and self.uncertainty.horizontal_nm is None:
            raise ValueError("a positioned record must state horizontal uncertainty")
        return self


def load_registry(path: str | Path) -> list[EvidenceRecord]:
    """Load a JSON-lines registry; ids must be unique."""
    recs: list[EvidenceRecord] = []
    for n, line in enumerate(Path(path).read_text().splitlines(), 1):
        if line.strip() and not line.lstrip().startswith("#"):
            try:
                recs.append(EvidenceRecord.model_validate(json.loads(line)))
            except Exception as e:
                raise ValueError(f"{path}:{n}: {e}") from e
    ids = [r.id for r in recs]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        raise ValueError(f"duplicate evidence ids: {sorted(dupes)}")
    return recs
