from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from test_agent.schemas.agent_schemas.prd_agent_schemas import (
    ProductAnalyzerAgentState,
)
from test_agent.agents.prd_agent.insights_extractor_agent import (
    InsightsExtractorAgent,
    InsigntsExtractorState,
)
from test_agent.document.document_processor import chunk_markdown_doument
from test_agent.agents.prd_agent.prompt_templates import (
    PRD_INSIGHTS_REFLECTOR_TEMPLATE,
    INSIGHTS_DEDUPLICATION_TEMPLATE,
)
from test_agent.llm.model_manager import ModelManager
from test_agent.agents.prd_agent.insight_tools import (
    tool_node,
    add_concern,
    add_product_insight,
    delete_concern,
    delete_product_insight,
)


class ProductAnalyzerAgent:

    def __init__(self):
        self.build_agent()

    def chunk_documents(
        self, state: ProductAnalyzerAgentState
    ) -> ProductAnalyzerAgentState:
        updated_documents = [
            doc.model_copy(update={"chunks": chunk_markdown_doument(doc.content)})
            for doc in state.documents
        ]
        return {"documents": updated_documents}

    def insights_extraction_orchestrator(
        self, state: ProductAnalyzerAgentState
    ) -> ProductAnalyzerAgentState:
        return [
            Send(
                "extract_insights",
                InsigntsExtractorState(
                    prd_text=chunk.page_content, config={"MAX_REFLECTION_COUNTER": 2}, prd_scope="CHUNK"
                ),
            )
            for chunk in state.documents[0].chunks
        ]

    def deduplicate_insights(
        self, state: ProductAnalyzerAgentState
    ) -> ProductAnalyzerAgentState:

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

    def reflect_insights(
        self, state: ProductAnalyzerAgentState
    ) -> ProductAnalyzerAgentState:

        reflection_counter = state.var.get("reflection_counter", 0)
        reflection_counter += 1

        insights_llm = ModelManager.get_instance().bind_tools(
            [add_product_insight, add_concern]
        )
        chain = PRD_INSIGHTS_REFLECTOR_TEMPLATE | insights_llm
        response = chain.invoke(
            {
                "markdown_prd": state.documents[0].content,
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
        return {
            "messages": [response],
            "var": {"reflection_counter": reflection_counter},
        }

    def should_reflect(self, state: ProductAnalyzerAgentState) -> bool:

        if state.var.get("reflection_counter", 1) <= state.config.get(
            "MAX_REFLECTION_COUNTER", 3
        ):
            return True
        return False

    def review_insights(
        self, state: ProductAnalyzerAgentState
    ) -> ProductAnalyzerAgentState:
        print("**" * 10)
        print("REVIEW PHASE")
        print("**" * 10)
        print("\n\n")

        print("==" * 30)
        print("INSIGHTS")
        print("==" * 30)
        print("\n\n")

        for insight in state.insights:
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

        self.insight_extractor = InsightsExtractorAgent()
        graph = StateGraph(ProductAnalyzerAgentState)
        graph.add_node("chunk_documents", self.chunk_documents)
        graph.add_node("extract_insights", self.insight_extractor.invoke)
        graph.add_node("deduplicate_insights", self.deduplicate_insights)
        graph.add_node("delete_insights_tool_node", tool_node)
        graph.add_node("reflect_insights", self.reflect_insights)
        graph.add_node("update_insights_tool_node", tool_node)
        graph.add_node("review_insights", self.review_insights)

        graph.add_edge(START, "chunk_documents")
        graph.add_conditional_edges(
            "chunk_documents",
            self.insights_extraction_orchestrator,
            ["extract_insights"],
        )
        graph.add_edge("extract_insights", "deduplicate_insights")
        graph.add_edge("deduplicate_insights", "delete_insights_tool_node")
        graph.add_edge("delete_insights_tool_node", "reflect_insights")
        graph.add_conditional_edges("reflect_insights", self.should_reflect, {
            True: "update_insights_tool_node",
            False: "review_insights"
        })
        graph.add_edge("update_insights_tool_node", "reflect_insights")
        graph.add_edge("review_insights", END)

        self.agent = graph.compile()
        print(self.agent.get_graph().draw_ascii())
        self.agent.get_graph().draw_mermaid_png(output_file_path="graph.png")

    def invoke(self, state: ProductAnalyzerAgentState) -> ProductAnalyzerAgentState:

        if not state.documents or len(state.documents) < 0:
            raise ValueError("No document found in Agent State")

        result = self.agent.invoke(state)
        return result
