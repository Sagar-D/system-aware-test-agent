from pydantic import BaseModel, Field
from uuid import UUID
from typing import List
from enum import Enum
from test_agent.schemas.agent_schemas.prd_agent_schemas import (
    Priority,
    FlowType,
    InsightStatus,
    ConfidenceLevel,
    ConcernType,
    ConcernSeverity,
    ConcernStatus,
)


class GenerateProductInsightsRequest(BaseModel):
    class Config:
        extra = "forbid"

    project_id: UUID
    release_id: UUID
    document_ids: List[UUID]


class ProductInsightGenerationStatus(str, Enum):
    INITIATED = "INITIATED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class GenerateProductInsightsResponse(BaseModel):
    class Config:
        extra = "forbid"

    document_id: UUID
    status: ProductInsightGenerationStatus
    message: str = ""


class ProductInsightCreate(BaseModel):
    class Config:
        extra = "forbid"

    title: str = Field(..., description="Short title describing the product flow")

    description: str = Field(
        ..., description="High-level description of the product intent"
    )

    flow_type: FlowType = Field(..., description="Type of product flow")

    priority: Priority = Field(..., description="Business priority of the flow")

    actors: List[str] = Field(
        default_factory=list, description="Actors involved in this product flow"
    )

    inputs: List[str] = Field(
        default_factory=list,
        description="Conceptual inputs to the flow (no technical schemas)",
    )

    expected_outcomes: List[str] = Field(
        ..., description="Expected observable outcomes of the flow"
    )

    preconditions: List[str] = Field(
        default_factory=list,
        description="Conditions that must be true before the flow starts",
    )

    postconditions: List[str] = Field(
        default_factory=list, description="Conditions expected after the flow completes"
    )

    business_rules: List[str] = Field(
        default_factory=list, description="Business rules that must be enforced"
    )

    assumptions: List[str] = Field(
        default_factory=list,
        description="Explicit assumptions due to missing or unclear information",
    )

    non_goals: List[str] = Field(
        default_factory=list,
        description="Explicitly out-of-scope behaviors for this flow",
    )

    source_document: UUID | None = None

    status: InsightStatus = Field(
        default=InsightStatus.PROPOSED,
        description="Current review status of the product insight",
    )

    confidence_level: ConfidenceLevel = Field(
        default=ConfidenceLevel.MEDIUM,
        description="Confidence in correctness of this insight",
    )


class CreateProductInsightRequest(BaseModel):
    class Config:
        extra = "forbid"

    project_id: UUID
    release_id: UUID
    document_id: UUID
    insights: List[ProductInsightCreate]


class ProductConcernCreate(BaseModel):
    class Config:
        extra = "forbid"

    related_product_insight_id: UUID | None = Field(
        None, description="Product insight this concern is related to (if applicable)"
    )

    type: ConcernType = Field(..., description="Type of concern")
    severity: ConcernSeverity = Field(..., description="Severity level of the concern")

    description: str = Field(..., description="Description of the concern or ambiguity")

    impact: str | None = Field(
        None, description="Impact of this concern on system understanding or testing"
    )

    questions: List[str] = Field(
        default_factory=list, description="Explicit clarification questions raised"
    )

    raised_by: str = Field(
        default="system", description="Who raised the concern (system or human)"
    )

    status: ConcernStatus = Field(
        default=ConcernStatus.OPEN, description="Current status of the concern"
    )

    source_document: UUID = Field(
        None,
        description="Source document ids from which this concern originated",
    )


class CreateProductConcernRequest(BaseModel):
    class Config:
        extra = "forbid"

    project_id: UUID
    release_id: UUID
    document_id: UUID
    concerns: List[ProductConcernCreate]


class ProductInsightUpdate(BaseModel):
    class Config:
        extra = "forbid"

    title: str | None = None
    description: str | None = None
    flow_type: FlowType | None = None
    priority: Priority | None = None
    actors: List[str] | None = None
    inputs: List[str] | None = None
    expected_outcomes: List[str] | None = None
    preconditions: List[str] | None = None
    postconditions: List[str] | None = None
    business_rules: List[str] | None = None
    assumptions: List[str] | None = None
    non_goals: List[str] | None = None
    source_document: UUID | None = None
    status: InsightStatus | None = None
    confidence_level: ConfidenceLevel | None = None


class ProductConcernUpdate(BaseModel):
    class Config:
        extra = "forbid"

    related_product_insight_id: UUID | None = None
    type: ConcernType | None = None
    severity: ConcernSeverity | None = None
    description: str | None = None
    impact: str | None = None
    questions: List[str] | None = None
    raised_by: str | None = None
    status: ConcernStatus | None = None
    source_document: UUID | None = None
