from typing import List

from pydantic import BaseModel, ConfigDict, Field, field_validator, RootModel
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
        ...,
        description="True if start_time falls on the queried date",
        examples=[False],
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


class BodyListItem(BaseModel):
    """Maps to the item schema under bodyList — all four fields required."""

    model_config = ConfigDict(extra="forbid")

    name: str
    id: str
    isNew: bool
    type: str


class BodiesByDepartmentResponse(BaseModel):
    """Flat response — no envelope."""

    model_config = ConfigDict(extra="forbid")

    totalBodies: int = Field(..., ge=0)
    newBodies: int = Field(..., ge=0)
    bodyList: List[BodyListItem] = Field(default_factory=list)


class DepartmentItem(BaseModel):
    id: str
    name: str
    isNew: bool = False
    hasData: bool = False


class DepartmentsByPortfolioResponse(BaseModel):
    totalDepartments: int = 0
    newDepartments: int = 0
    departmentList: List[DepartmentItem] = Field(default_factory=list)


class MinisterListItem(BaseModel):
    """Matches the dict shape returned by enrich_person_data."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="Minister ID", examples=["cit-xx"])
    name: str = Field(..., description="Minister name", examples=["Test Minister"])
    isNew: bool = Field(
        ...,
        description="True if start_time falls on the queried date",
        examples=[False],
    )
    isPresident: bool = Field(
        ...,
        description="True if this minister is the current president",
        examples=[False],
    )


class PortfolioListItem(BaseModel):
    """Matches the dict shape returned by enrich_portfolio_item."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="Portfolio ID", examples=["port-xx"])
    name: str = Field(
        ..., description="Portfolio name", examples=["Ministry of Finance"]
    )
    type: str = Field(
        ...,
        description="Portfolio kind.minor value, e.g. StateMinister",
        examples=["StateMinister"],
    )
    isNew: bool = Field(
        ...,
        description="True if this portfolio is new as of the selected date",
        examples=[False],
    )
    ministers: List[MinisterListItem] = Field(default_factory=list)


class ActivePortfolioListResponse(BaseModel):
    """Flat response — no envelope."""

    model_config = ConfigDict(extra="forbid")

    NoOfCabinetMinistries: int = Field(..., ge=0, examples=[20])
    NoOfStateMinistries: int = Field(..., ge=0, examples=[5])
    newMinistries: int = Field(..., ge=0, examples=[1])
    newMinisters: int = Field(..., ge=0, examples=[1])
    ministriesUnderPresident: int = Field(..., ge=0, examples=[2])
    portfolioList: List[PortfolioListItem] = Field(default_factory=list)


class PrimeMinisterItem(BaseModel):
    """Matches enrich_person_data output after isPresident is dropped and term is added."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="Prime Minister ID", examples=["cit-xx"])
    name: str = Field(..., description="Prime Minister name", examples=["Test PM"])
    isNew: bool = Field(
        ...,
        description="True if start_time falls on the queried date",
        examples=[False],
    )
    term: str = Field(
        ..., description="Formatted term string", examples=["2020 - 2022"]
    )


class PrimeMinisterResponse(BaseModel):
    """Envelope response — body is empty when no active prime minister is found."""

    model_config = ConfigDict(extra="forbid")

    body: PrimeMinisterItem | dict = Field(
        ..., description="Prime minister details, or {} if none found for the date"
    )


class EntityNamesResponse(RootModel[dict[str, str]]):
    """Maps each entity ID to its decoded display name."""
