from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import date as _date

class Date(BaseModel):
    """
    Request body carrying the as-of date for point-in-time lookups.
    """

    date: str = Field(
        ...,
        description="Date to query persons as-of.",
        examples=["2026-04-21"],
    )

    @field_validator("date")
    @classmethod
    def _validate_iso_date(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("date must not be empty")
        try:
            _date.fromisoformat(value)
        except ValueError as exc:
            raise ValueError("date must be in ISO-8601 format (YYYY-MM-DD)") from exc
        return value


class PersonListItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="Person ID", examples=["cit-xx"])
    name: str = Field(
        ..., description="Fully resolved, human-readable name", examples=["Test Person"]
    )
    isNew: bool = Field(
        ..., description="True if start_time falls on the queried date", examples=[False]
    )
    isPresident: bool = Field(
        ...,
        description="True if this person is the currently selected president",
        examples=[False],
    )


class PortfolioPersonsResponse(BaseModel):

    totalCount: int = Field(
        ..., ge=0, description="Total number of People' in Portfolio", examples=[1]
    )
    newCount: int = Field(
        ..., ge=0, description="Count of persons where is_new is true", examples=[0]
    )
    personList: List[PersonListItem]