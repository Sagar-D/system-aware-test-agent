from pydantic import BaseModel, UUID4, Field
from enum import Enum
from typing import List, Dict, Any, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
import operator


class Chunk(BaseModel):
    id: str
    content: str
    parent_doc_id: UUID4


class Document(BaseModel):
    id: str
    content: str
    version: str = None
    file_path: str = None
    chunks: List[Chunk] = None


class FlowType(str, Enum):
    user_flow = "user_flow"
    backend_flow = "backend_flow"
    data_flow = "data_flow"


class Priority(str, Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


class InsightStatus(str, Enum):
    draft = "draft"
    needs_clarification = "needs_clarification"
    approved = "approved"
    locked = "locked"


class ConfidenceLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class ProductInsight(BaseModel):
    id: str = Field(..., description="Unique identifier for the product insight")

    title: str = Field(..., description="Short title describing the product flow")
    description: str = Field(
        ..., description="High-level description of the product intent"
    )

    flow_type: FlowType = Field(None, description="Type of product flow")

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

    source_documents: List[str] = Field(
        default_factory=list,
        description="Source document ids from which this insight was derived",
    )

    status: InsightStatus = Field(
        default=InsightStatus.draft,
        description="Current review status of the product insight",
    )

    confidence_level: ConfidenceLevel = Field(
        default=ConfidenceLevel.medium,
        description="Confidence in correctness of this insight",
    )


class ConcernType(str, Enum):
    missing_information = "missing_information"
    ambiguity = "ambiguity"
    conflict = "conflict"
    scope_gap = "scope_gap"
    other = "other"


class ConcernSeverity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class ConcernStatus(str, Enum):
    open = "open"
    clarified = "clarified"
    accepted_risk = "accepted_risk"
    closed = "closed"


class Concern(BaseModel):
    id: str = Field(..., description="Unique identifier for the concern")

    related_product_insight_id: str | None = Field(
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
        default=ConcernStatus.open, description="Current status of the concern"
    )

    source_documents: List[str] = Field(
        default_factory=list,
        description="Source document ids from which this concern originated",
    )


class BaseInsightsSchema(BaseModel) :
    insights: Annotated[List[ProductInsight], operator.add] = Field(
        default_factory=list
    )
    concerns: Annotated[List[Concern], operator.add] = Field(default_factory=list)
    messages: Annotated[List[BaseMessage], add_messages] = Field(default_factory=list)
    config: Annotated[Dict[str, Any], operator.or_] = Field(default_factory=dict)
    var: Annotated[Dict[str, Any], operator.or_] = Field(default_factory=dict)

class InsigntsExtractorState(BaseInsightsSchema):
    prd_text: str
    prd_scope: str
    

class ProductAnalyzerAgentState(BaseInsightsSchema):
    project_id: str
    release_id: str
    documents: List[Document]
    deleted_insights: Annotated[List[str], operator.add] = Field(default_factory=list)
    deleted_concerns: Annotated[List[str], operator.add] = Field(default_factory=list)