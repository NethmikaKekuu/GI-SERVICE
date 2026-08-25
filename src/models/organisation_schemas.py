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


class DepartmentHistoryItem(BaseModel):
    """Matches one collapsed timeline entry from department_history_timeline."""

    model_config = ConfigDict(extra="forbid")

    ministry_id: str = Field(..., description="Ministry ID", examples=["min-xx"])
    ministry_name: str = Field(
        ..., description="Ministry name", examples=["Ministry of Finance"]
    )
    minister_id: str | None = Field(
        default=None,
        description="Minister ID for this period, null if no minister/president could be resolved",
        examples=["cit-xx"],
    )
    minister_name: str | None = Field(
        default=None,
        description="Minister name for this period, null if no minister/president could be resolved",
        examples=["Test Minister"],
    )
    period: str = Field(
        ..., description="Formatted period string", examples=["2020 - 2022"]
    )


class DepartmentHistoryResponse(RootModel[List[DepartmentHistoryItem]]):
    """Timeline entries, most recent first."""


class GazetteEntry(BaseModel):
    """One gazette entry within a tenure's gazetteList."""

    model_config = ConfigDict(extra="forbid")

    date: str = Field(..., description="Gazette publish date", examples=["2020-08-15"])
    idList: List[str] = Field(
        ...,
        description="Decoded gazette IDs published on this date",
        examples=[["EXTGZT-001", "EXTGZT-002"]],
    )


class Tenure(BaseModel):
    """One presidential term."""

    model_config = ConfigDict(extra="forbid")

    startDate: str = Field(..., description="Term start date", examples=["2015-01-08"])
    endDate: str = Field(
        ...,
        description="Term end date, empty string if ongoing/unknown",
        examples=["2020-11-14"],
    )
    gazetteList: List[GazetteEntry] = Field(default_factory=list)


class PresidentItem(BaseModel):
    """One president with all their terms."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="President ID", examples=["cit-xx"])
    name: str = Field(
        ...,
        description="President name, empty string if lookup failed",
        examples=["Test President"],
    )
    tenureList: List[Tenure] = Field(default_factory=list)


class PresidentsResponse(BaseModel):
    """Envelope response."""

    model_config = ConfigDict(extra="forbid")

    body: List[PresidentItem] = Field(default_factory=list)


class CabinetFlowNode(BaseModel):
    """One node in the cabinet flow graph — a minister at a specific chart date."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="Minister entity ID", examples=["cit-xx"])
    time: str = Field(
        ..., description="Date this node represents", examples=["2020-01-01"]
    )
    name: str | None = Field(
        default=None,
        description="Minister name, null if the name lookup failed",
        examples=["Test Minister"],
    )


class CabinetFlowLink(BaseModel):
    """One link between two nodes representing departments that moved between ministers."""

    model_config = ConfigDict(extra="forbid")

    source: int = Field(
        ..., description="Index into nodes for the source minister", examples=[0]
    )
    target: int = Field(
        ..., description="Index into nodes for the target minister", examples=[1]
    )
    value: int = Field(
        ..., ge=0, description="Number of departments that moved", examples=[3]
    )
    departmentIds: List[str] = Field(
        ...,
        description="Department IDs that moved along this link",
        examples=[["dep-001", "dep-002"]],
    )


class CabinetFlowDateStatus(BaseModel):
    """Per-date processing status. departmentsCount is set for ok/no_data; message is set for error."""

    model_config = ConfigDict(extra="forbid")

    date: str = Field(..., description="The queried date", examples=["2020-01-01"])
    status: str = Field(..., description="ok | no_data | error", examples=["ok"])
    departmentsCount: int | None = Field(
        default=None,
        description="Number of departments found, present for ok/no_data",
        examples=[5],
    )
    message: str | None = Field(
        default=None,
        description="Error message, present only when status is error",
        examples=["..."],
    )


class CabinetFlowResponse(BaseModel):
    """Flat response — no envelope."""

    model_config = ConfigDict(extra="forbid")

    nodes: List[CabinetFlowNode] = Field(default_factory=list)
    links: List[CabinetFlowLink] = Field(default_factory=list)
    dates: List[CabinetFlowDateStatus] = Field(default_factory=list)
