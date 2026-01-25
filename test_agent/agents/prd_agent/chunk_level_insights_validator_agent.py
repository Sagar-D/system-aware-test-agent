from langgraph.graph import StateGraph, START, END
from langchain.messages import ToolMessage
from test_agent.schemas.agent_schemas.prd_agent_schemas import (
    InsigntsValidatorState,
    ProductInsight,
    Concern,
    PrdAnalyzerAgentState,
)
from uuid6 import uuid7
from test_agent.llm.model_manager import ModelManager
from test_agent.agents.prd_agent.prompt_templates import (
    CHUNK_LEVEL_PRD_INSIGHTS_VALIDATOR_TEMPLATE,
)
from test_agent.agents.prd_agent.insight_tools import (
    add_concern,
    add_product_insight,
)


class InsightsValidatorAgent:

    def __init__(self):
        self.build_agent()

    def validate_insights(
        self, state: InsigntsValidatorState
    ) -> InsigntsValidatorState:

        insights_validator_llm = ModelManager.get_instance().bind_tools(
            [add_product_insight, add_concern]
        )
        chain = CHUNK_LEVEL_PRD_INSIGHTS_VALIDATOR_TEMPLATE | insights_validator_llm
        response = chain.invoke(
            {
                "markdown_prd": state.document.page_content,
                "chunk": state.prd_chunk,
                "existing_product_insights": "\n".join(
                    [
                        f"{i+1}. {insight.description}"
                        for i, insight in enumerate(state.insights)
                    ]
                ),
                "existing_concerns": "\n".join(
                    [
                        f"{i+1}. {concern.description}"
                        for i, concern in enumerate(state.concerns)
                    ]
                ),
            }
        )
        return {"messages": [response]}

    def tool_node(self, state: InsigntsValidatorState) -> InsigntsValidatorState:
        insights = []
        concerns = []
        tool_messages = []

        for tool_call in state.messages[-1].tool_calls:
            if tool_call["name"] == "add_product_insight":
                try:
                    tool_call["args"]["id"] = uuid7()
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
                    tool_call["args"]["id"] = uuid7()
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

        return {
            "new_insights": insights,
            "new_concerns": concerns,
            "tool_messages": tool_messages,
        }

    def build_agent(self):

        graph = StateGraph(InsigntsValidatorState)
        graph.add_node("validate_insights", self.validate_insights)
        graph.add_node("tool_node", self.tool_node)

        graph.add_edge(START, "validate_insights")
        graph.add_edge("validate_insights", "tool_node")
        graph.add_edge("tool_node", END)
        self.agent = graph.compile()

    def invoke(self, state: InsigntsValidatorState) -> dict:

        if not state.prd_chunk or len(state.prd_chunk) < 0:
            raise ValueError(
                "No PRD / PRD prd_text found in Agent State to Extract Insights"
            )
        result = self.agent.invoke(state)

        return {
            "insights": result["new_insights"],
            "conerns": result["new_concerns"],
            "messages": result["tool_messages"],
        }
