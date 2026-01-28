from uuid import UUID
from typing import List
from langchain_core.documents import Document
from test_agent.db.repositories.document import (
    get_documents_by_ids,
    get_document_chunks,
)
from test_agent.agents.prd_agent.prd_analyzer_agent import (
    PrdAnalyzerAgent,
    PrdAnalyzerAgentState,
)
from test_agent.schemas.agent_schemas.prd_agent_schemas import PrdDocument
from test_agent.db.repositories.product import create_insights, create_concerns


def generate_insights(document_ids: List[UUID], project_id: UUID, release_id: UUID):

    loaded_documents = get_documents_by_ids(document_ids)

    for loaded_doc in loaded_documents:
        ## Update job_status table to IN_PROGRESS for document_id
        loaded_doc["chunks"] = [
            Document(chunk["content"], id=chunk["id"])
            for chunk in get_document_chunks(loaded_doc["id"])
        ]

        document = PrdDocument(
            id=loaded_doc["id"],
            hash=loaded_doc["hash"],
            page_content=loaded_doc["content"],
            chunks=loaded_doc["chunks"],
        )

        agent_state = PrdAnalyzerAgentState(
            project_id=str(project_id),
            release_id=str(release_id),
            document=document,
        )

        agent = PrdAnalyzerAgent()
        result = agent.invoke(state=agent_state)

        insight_ids = create_insights(
            project_id=project_id,
            release_id=release_id,
            document_id=loaded_doc["id"],
            product_insights=result["insights"],
        )

        concern_ids = create_concerns(
            project_id=project_id,
            release_id=release_id,
            document_id=loaded_doc["id"],
            product_concerns=result["concerns"],
        )
        ## Update job_status table to COMPLETED for document_id
