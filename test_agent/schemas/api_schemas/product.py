from pydantic import BaseModel, Field
from uuid import UUID
from typing import List
from enum import Enum
from test_agent.schemas.agent_schemas.prd_agent_schemas import (
    Priority,
    FlowType,
    InsightStatus,
    ConfidenceLevel,
)


class GenerateProductInsightsRequest(BaseModel):
    project_id: UUID
    release_id: UUID
    document_ids: List[UUID]


class ProductInsightGenerationStatus(str, Enum):
    INITIATED = "INITIATED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class GenerateProductInsightsResponse(BaseModel):
    document_id: UUID
    status: ProductInsightGenerationStatus
    message: str = ""


class ProductInsight(BaseModel):

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
    project_id: UUID
    release_id: UUID
    document_id: UUID
    insights: List[ProductInsight]
