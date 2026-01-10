from langgraph.graph import StateGraph, START, END
from test_agent.schemas.agent_schemas.prd_agent_schemas import (
    InsigntsExtractorState,
)
from test_agent.llm.model_manager import ModelManager
from test_agent.agents.prd_agent.prompt_templates import (
    COMPLETE_PRD_INSIGHTS_GENERATOR_TEMPLATE,
    CHUNK_LEVEL_PRD_INSIGHTS_GENERATOR_TEMPLATE,
)
from test_agent.agents.prd_agent.insight_tools import tool_node, add_concern, add_product_insight


class InsightsExtractorAgent:

    def __init__(self):
        self.build_agent()

    def extract_insights(
        self, state: InsigntsExtractorState
    ) -> InsigntsExtractorState:

        insights_llm = ModelManager.get_instance().bind_tools(
            [add_product_insight, add_concern]
        )

        prompt_template = (
            COMPLETE_PRD_INSIGHTS_GENERATOR_TEMPLATE
            if state.prd_scope.upper() == "COMPLETE"
            else CHUNK_LEVEL_PRD_INSIGHTS_GENERATOR_TEMPLATE
        )
        chain = prompt_template | insights_llm
        response = chain.invoke({"markdown_prd": state.prd_text})
        return {"messages": [response]}

    def build_agent(self):

        graph = StateGraph(InsigntsExtractorState)
        graph.add_node("extract_insights", self.extract_insights)
        graph.add_node("tool_node", tool_node)

        graph.add_edge(START, "extract_insights")
        graph.add_edge("extract_insights", "tool_node")
        graph.add_edge("tool_node", END)
        self.agent = graph.compile()

    def invoke(self, state: InsigntsExtractorState) -> dict:

        if not state.prd_text or len(state.prd_text) < 0:
            raise ValueError(
                "No PRD / PRD prd_text found in Agent State to Extract Insights"
            )
        state.prd_scope = state.prd_scope.upper()
        if state.prd_scope not in ["COMPLETE", "CHUNK"]:
            raise ValueError(
                f"Unsupported PRD scope '{state.prd_scope}' passed. Supported scope ['COMPLETE', 'CHUNK']"
            )
        result = self.agent.invoke(state)

        return {
            "insights": result["insights"],
            "conerns": result["concerns"],
            "messages": result["messages"],
        }
