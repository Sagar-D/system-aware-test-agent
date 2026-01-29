from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Dict, Any, Annotated
from uuid import UUID
from langchain_core.messages import BaseMessage
from langchain_core.documents import Document
from langgraph.graph import add_messages
import operator


class PrdDocument(BaseModel):
    id: UUID
    hash: str
    page_content: str
    version: str = None
    file_path: str = None
    chunks: List[Document] = None


class FlowType(str, Enum):
    user_flow = "user_flow"
    backend_flow = "backend_flow"
    data_flow = "data_flow"


class Priority(str, Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


class InsightStatus(str, Enum):
    PROPOSED = "PROPOSED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ConfidenceLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ProductInsight(BaseModel):
    id: UUID = Field(..., description="Unique identifier for the product insight")

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

    source_document: UUID = Field(
        None,
        description="Source document ids from which this insight was derived",
    )

    status: InsightStatus = Field(
        default=InsightStatus.PROPOSED,
        description="Current review status of the product insight",
    )

    confidence_level: ConfidenceLevel = Field(
        default=ConfidenceLevel.MEDIUM,
        description="Confidence in correctness of this insight",
    )


class ConcernType(str, Enum):
    missing_information = "missing_information"
    ambiguity = "ambiguity"
    conflict = "conflict"
    scope_gap = "scope_gap"
    other = "other"


class ConcernSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ConcernStatus(str, Enum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"


class ProductConcern(BaseModel):
    id: UUID = Field(..., description="Unique identifier for the concern")

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


class BaseInsightsSchema(BaseModel):
    document: PrdDocument
    insights: Annotated[List[ProductInsight], operator.add] = Field(
        default_factory=list
    )
    concerns: Annotated[List[ProductConcern], operator.add] = Field(
        default_factory=list
    )
    messages: Annotated[List[BaseMessage], add_messages] = Field(default_factory=list)
    config: Annotated[Dict[str, Any], operator.or_] = Field(default_factory=dict)
    var: Annotated[Dict[str, Any], operator.or_] = Field(default_factory=dict)


class InsigntsValidatorState(BaseInsightsSchema):
    prd_chunk: str
    new_insights: Annotated[List[ProductInsight], operator.add] = Field(
        default_factory=list
    )
    new_concerns: Annotated[List[ProductConcern], operator.add] = Field(
        default_factory=list
    )
    tool_messages: Annotated[List[BaseMessage], add_messages] = Field(
        default_factory=list
    )


class PrdAnalyzerAgentState(BaseInsightsSchema):
    project_id: str
    release_id: str
    deleted_insights: Annotated[List[UUID], operator.add] = Field(default_factory=list)
    deleted_concerns: Annotated[List[UUID], operator.add] = Field(default_factory=list)
