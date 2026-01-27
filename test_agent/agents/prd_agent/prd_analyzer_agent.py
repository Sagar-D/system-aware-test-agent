from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from langchain.messages import ToolMessage
from uuid6 import uuid7
from typing import Dict
from test_agent.schemas.agent_schemas.prd_agent_schemas import (
    PrdAnalyzerAgentState,
    InsigntsValidatorState,
    ProductInsight,
    Concern,
)
from test_agent.agents.prd_agent.chunk_level_insights_validator_agent import (
    InsightsValidatorAgent,
)
from test_agent.agents.prd_agent.prompt_templates import (
    PRD_INSIGHTS_EXTRACTOR_TEMPLATE,
    PRD_INSIGHTS_REFLECTOR_TEMPLATE,
    INSIGHTS_DEDUPLICATION_TEMPLATE,
)
from test_agent.llm.model_manager import ModelManager
from test_agent import config
from test_agent.agents.prd_agent.insight_tools import (
    add_concern,
    add_product_insight,
    delete_concern,
    delete_product_insight,
)


class PrdAnalyzerAgent:

    def __init__(self):
        self.build_agent()

    def extract_insights(self, state: PrdAnalyzerAgentState) -> PrdAnalyzerAgentState:

        insights_llm = ModelManager.get_instance().bind_tools(
            [add_product_insight, add_concern]
        )
        chain = PRD_INSIGHTS_EXTRACTOR_TEMPLATE | insights_llm
        response = chain.invoke({"markdown_prd": state.document.page_content})
        return {"messages": [response]}

    def tool_node(self, state: PrdAnalyzerAgentState) -> PrdAnalyzerAgentState:
        insights = []
        concerns = []
        tool_messages = []
        deleted_insights = []
        deleted_concerns = []
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
                    print(
                        f"Failed to add an insight_id to delete list \n Exception : {e}"
                    )
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
                    print(
                        f"Failed to add a concern_id to delete list \n Exception : {e}"
                    )
        return {
            "insights": insights,
            "concerns": concerns,
            "messages": tool_messages,
            "deleted_insights": deleted_insights,
            "deleted_concern": deleted_concerns,
        }

    def should_reflect(self, state: PrdAnalyzerAgentState) -> bool:

        if state.var.get("reflection_counter", 0) < state.config.get(
            "MAX_REFLECTION_COUNTER", config.MAX_REFLECTION_COUNT
        ):
            return True
        return False

    def reflect_insights(self, state: PrdAnalyzerAgentState) -> PrdAnalyzerAgentState:

        reflection_counter = state.var.get("reflection_counter", 0)
        reflection_counter += 1

        insights_llm = ModelManager.get_instance().bind_tools(
            [add_product_insight, add_concern]
        )
        chain = PRD_INSIGHTS_REFLECTOR_TEMPLATE | insights_llm
        response = chain.invoke(
            {
                "markdown_prd": state.document.page_content,
                "existing_product_insights": "\n".join(
                    [
                        f"{i+1}. {insight.description}"
                        for i, insight in enumerate(state.insights)
                        if insight.id not in state.deleted_insights
                    ]
                ),
                "existing_concerns": "\n".join(
                    [
                        f"{i+1}. {concern.description}"
                        for i, concern in enumerate(state.concerns)
                        if concern.id not in state.deleted_concerns
                    ]
                ),
            }
        )
        return {
            "messages": [response],
            "var": {"reflection_counter": reflection_counter},
        }

    def chunk_documents(self, state: PrdAnalyzerAgentState) -> PrdAnalyzerAgentState:
        # document_chunks = chunk_markdown_document(state.document.page_content)
        # updated_document = state.document.model_copy(update={"chunks": document_chunks})
        # return {"document": updated_document}
        return {}

    def chunk_level_validation_orchestrator(
        self, state: PrdAnalyzerAgentState
    ) -> PrdAnalyzerAgentState:
        return [
            Send(
                "chunk_level_insight_validator",
                InsigntsValidatorState(
                    prd_chunk=chunk.page_content,
                    document=state.document,
                    insights=state.insights,
                    concerns=state.concerns,
                ),
            )
            for chunk in state.document.chunks
        ]

    def deduplicate_insights(
        self, state: PrdAnalyzerAgentState
    ) -> PrdAnalyzerAgentState:

        deduplicator_llm = ModelManager.get_instance().bind_tools(
            [delete_product_insight, delete_concern]
        )

        chain = INSIGHTS_DEDUPLICATION_TEMPLATE | deduplicator_llm
        response = chain.invoke(
            {
                "insights_list": [
                    f"{insight.id} - {insight.description}"
                    for insight in state.insights
                ],
                "concerns_list": [
                    f"{concern.id} - {concern.description}"
                    for concern in state.concerns
                ],
            }
        )
        return {"messages": [response]}

    def review_insights(self, state: PrdAnalyzerAgentState) -> PrdAnalyzerAgentState:

        print("**" * 10)
        print("REVIEW PHASE")
        print("**" * 10)
        print("\n\n")

        print("==" * 30)
        print("INSIGHTS")
        print("==" * 30)
        print("\n\n")

        for insight in state.insights:
            if insight.id not in state.deleted_insights:
                print("--" * 30)
                print(f"{insight.title = }")
                print(f"{insight.description = }")
                print(f"{insight.actors = }")
                print(f"{insight.inputs = }")
                print(f"{insight.expected_outcomes = }")
                print("--" * 30)
                print("\n")

        print("==" * 30)
        print("CONCERNS")
        print("==" * 30)
        print("\n\n")

        for concern in state.concerns:
            if concern.id not in state.deleted_concerns:
                print("--" * 30)
                print(f"{concern.description = }")
                print(f"{concern.impact = }")
                print(f"{concern.questions = }")
                print(f"{concern.raised_by = }")
                print(f"{concern.related_product_insight_id = }")
                print(f"{concern.severity = }")
                print("--" * 30)
                print("\n")

    def build_agent(self):

        self.chunk_level_insight_validator = InsightsValidatorAgent()
        graph = StateGraph(PrdAnalyzerAgentState)
        graph.add_node("extract_insights", self.extract_insights)
        graph.add_node("add_insights_tool_node", self.tool_node)
        graph.add_node("reflect_insights", self.reflect_insights)
        graph.add_node("update_insights_tool_node", self.tool_node)
        graph.add_node("chunk_documents", self.chunk_documents)
        graph.add_node(
            "chunk_level_insight_validator", self.chunk_level_insight_validator.invoke
        )
        graph.add_node("deduplicate_insights", self.deduplicate_insights)
        graph.add_node("delete_insights_tool_node", self.tool_node)
        graph.add_node("review_insights", self.review_insights)

        graph.add_edge(START, "extract_insights")
        graph.add_edge("extract_insights", "add_insights_tool_node")
        graph.add_conditional_edges(
            "add_insights_tool_node",
            self.should_reflect,
            {True: "reflect_insights", False: "chunk_documents"},
        )
        graph.add_edge("reflect_insights", "update_insights_tool_node")
        graph.add_conditional_edges(
            "update_insights_tool_node",
            self.should_reflect,
            {True: "reflect_insights", False: "chunk_documents"},
        )
        graph.add_conditional_edges(
            "chunk_documents",
            self.chunk_level_validation_orchestrator,
            ["chunk_level_insight_validator"],
        )
        graph.add_edge("chunk_level_insight_validator", "deduplicate_insights")
        graph.add_edge("deduplicate_insights", "delete_insights_tool_node")
        graph.add_edge("delete_insights_tool_node", "review_insights")
        graph.add_edge("review_insights", END)

        self.agent = graph.compile()
        print(self.agent.get_graph().draw_ascii())
        self.agent.get_graph().draw_mermaid_png(output_file_path="graph.png")

    def invoke(self, state: PrdAnalyzerAgentState) -> Dict:

        if not state.document or state.document.page_content.strip() == "":
            raise ValueError("No document found in Agent State")

        final_state = self.agent.invoke(state)

        result = {
            "project_id": final_state["project_id"],
            "release_id": final_state["release_id"],
            "document": final_state["document"],
            "insights": [insight for insight in final_state["insights"] if insight.id not in final_state["deleted_insights"]],
            "concerns": [concern for concern in final_state["concerns"] if concern.id not in final_state["deleted_concerns"]]
        }

        return result
