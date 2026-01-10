from langchain.tools import tool
from langchain_core.messages import ToolMessage

from test_agent.schemas.agent_schemas.prd_agent_schemas import (
    ProductInsight,
    Concern,
    InsigntsExtractorState,
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


def tool_node(state: dict) -> dict:
    insights = []
    concerns = []
    tool_messages = []
    deleted_insights = []
    deleted_concerns = []
    for tool_call in state.messages[-1].tool_calls:
        if tool_call["name"] == "add_product_insight":
            try:
                tool_results = add_product_insight.invoke(tool_call["args"])
                insights.append(ProductInsight(**tool_results))
                tool_messages.append(
                    ToolMessage(
                        content="Successfully added Product Insight",
                        tool_call_id=tool_call["id"],
                    )
                )
            except Exception as e:
                print(f"Failed to add an insight to the list \n Exception : {e}")
        if tool_call["name"] == "add_concern":
            try:
                tool_results = add_concern.invoke(tool_call["args"])
                concerns.append(Concern(**tool_results))
                tool_messages.append(
                    ToolMessage(
                        content="Successfully added Concern",
                        tool_call_id=tool_call["id"],
                    )
                )
            except Exception as e:
                print(f"Failed to add a concern to the list \n Exception : {e}")

        if tool_call["name"] == "delete_product_insight":
            try:
                insight_id = delete_product_insight.invoke(tool_call["args"])
                deleted_insights.append(insight_id)
                tool_messages.append(
                    ToolMessage(
                        content="Successfully added a insight_id to delete_list",
                        tool_call_id=tool_call["id"],
                    )
                )
            except Exception as e:
                print(f"Failed to add an insight_id to delete list \n Exception : {e}")
        if tool_call["name"] == "delete_concern":
            try:
                concern_id = delete_concern.invoke(tool_call["args"])
                deleted_concerns.append(concern_id)
                tool_messages.append(
                    ToolMessage(
                        content="Successfully added a concern_id to delete_list",
                        tool_call_id=tool_call["id"],
                    )
                )
            except Exception as e:
                print(f"Failed to add a concern_id to delete list \n Exception : {e}")
    return {
        "insights": insights,
        "concerns": concerns,
        "messages": tool_messages,
        "deleted_insights": deleted_insights,
        "deleted_concern": deleted_concerns,
    }
