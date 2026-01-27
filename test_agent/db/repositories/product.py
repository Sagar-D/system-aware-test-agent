import sqlite3
from typing import List
from uuid import UUID
from test_agent import config
from test_agent.schemas.agent_schemas.prd_agent_schemas import ProductInsight, Concern


def create_insights(
    project_id: UUID,
    release_id: UUID,
    document_id: UUID,
    status: str,
    insights: List[ProductInsight],
) -> List[UUID]:

    data = [
        (
            str(insight.id),
            str(project_id),
            str(release_id),
            str(document_id),
            status,
            insight.model_dump_json(),
        )
        for insight in insights
    ]
    with sqlite3.connect(config.RELATIONAL_DB_NAME) as conn:

        conn.executemany(
            """INSERT OR REPLACE INTO product_insight 
            (id, project_id, release_id, document_id, status, details) VALUES (?,?,?,?,?,?)""",
            data,
        )


def create_concerns(
    project_id: UUID,
    release_id: UUID,
    document_id: UUID,
    status: str,
    concerns: List[Concern],
) -> List[UUID]:

    data = [
        (
            str(concern.id),
            str(project_id),
            str(release_id),
            str(document_id),
            status,
            concern.model_dump_json(),
        )
        for concern in concerns
    ]
    with sqlite3.connect(config.RELATIONAL_DB_NAME) as conn:

        conn.executemany(
            """INSERT OR REPLACE INTO product_concern
            (id, project_id, release_id, document_id, status, details) VALUES (?,?,?,?,?,?)""",
            data,
        )