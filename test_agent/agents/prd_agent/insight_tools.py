from langchain.tools import tool
from typing import Dict, List
from uuid6 import uuid7
from test_agent.schemas.agent_schemas.prd_agent_schemas import (
    ProductInsight,
    ProductConcern,
    InsightStatus,
    ConcernStatus,
)


@tool("add_product_insight", args_schema=ProductInsight)
def add_product_insight(**kwargs):
    """Add Product Insight to Product Insights Master List"""
    return kwargs


@tool("delete_product_insight")
def delete_product_insight(insight_id: str):
    """Delete Product Insight from Product Insights Master List"""
    return insight_id


@tool("add_concern", args_schema=ProductConcern)
def add_concern(**kwargs):
    """Add Concern to Concerns Master List"""
    return kwargs


@tool("delete_concern")
def delete_concern(concern_id: str):
    """Delete Concern from Concerns Master List"""
    return concern_id


def build_product_insight(
    raw_insight: Dict, source_document_id: List[str] = None
) -> ProductInsight:

    raw_insight["id"] = uuid7()
    raw_insight["status"] = InsightStatus.PROPOSED
    raw_insight["source_document"] = (
        source_document_id or raw_insight["source_document"]
    )
    return ProductInsight(**raw_insight)


def build_product_concern(
    raw_concern: Dict, source_document_id: str = None
) -> ProductInsight:

    raw_concern["id"] = uuid7()
    raw_concern["status"] = ConcernStatus.OPEN
    raw_concern["source_document"] = (
        source_document_id or raw_concern["source_document"]
    )
    raw_concern["related_product_insight_id"] = None
    return ProductConcern(**raw_concern)
