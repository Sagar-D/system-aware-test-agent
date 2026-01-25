from langchain.tools import tool

from test_agent.schemas.agent_schemas.prd_agent_schemas import (
    ProductInsight,
    Concern,
)


@tool("add_product_insight", args_schema=ProductInsight)
def add_product_insight(**kwargs):
    """Add Product Insight to Product Insights Master List"""
    return kwargs


@tool("delete_product_insight")
def delete_product_insight(insight_id: str):
    """Delete Product Insight from Product Insights Master List"""
    return insight_id


@tool("add_concern", args_schema=Concern)
def add_concern(**kwargs):
    """Add Concern to Concerns Master List"""
    return kwargs


@tool("delete_concern")
def delete_concern(concern_id: str):
    """Delete Concern from Concerns Master List"""
    return concern_id
