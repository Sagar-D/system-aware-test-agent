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

    for doc in loaded_documents:
        doc["chunks"] = [
            Document(chunk["content"], id=chunk["id"])
            for chunk in get_document_chunks(doc["id"])
        ]

    documents = [
        PrdDocument(
            id=doc["id"],
            hash=doc["hash"],
            page_content=doc["content"],
            chunks=doc["chunks"],
        )
        for doc in loaded_documents
    ]
    
    agent_state = PrdAnalyzerAgentState(
        project_id=str(project_id),
        release_id=str(release_id),
        document=documents[0],
    )

    agent = PrdAnalyzerAgent()
    result = agent.invoke(state=agent_state)

    create_insights(
        project_id=project_id,
        release_id=release_id,
        document_id=document_ids[0],
        status="PROPOSED",
        insights=result["insights"]
    )

    create_concerns(
        project_id=project_id,
        release_id=release_id,
        document_id=document_ids[0],
        status="OPEN",
        concerns=result["concerns"]
    )
