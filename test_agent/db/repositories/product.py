import sqlite3
from typing import List, Dict
from uuid import UUID
import json
from test_agent import config
from test_agent.schemas.agent_schemas.prd_agent_schemas import (
    ProductInsight,
    ProductConcern,
)
from test_agent.utils.common import is_valid_uuid
from test_agent.db.repositories.core import does_project_exist, does_release_exist
from test_agent.db.repositories.document import does_document_exist


def create_insights(
    project_id: UUID,
    release_id: UUID,
    document_id: UUID,
    product_insights: List[ProductInsight],
) -> List[UUID]:

    data = [
        (
            str(insight.id),
            str(project_id),
            str(release_id),
            str(document_id),
            insight.status,
            insight.model_dump_json(),
        )
        for insight in product_insights
    ]
    with sqlite3.connect(config.RELATIONAL_DB_NAME) as conn:

        conn.executemany(
            """INSERT OR REPLACE INTO product_insight 
            (id, project_id, release_id, document_id, status, details) VALUES (?,?,?,?,?,?)""",
            data,
        )
    return [insight.id for insight in product_insights]


def get_insights(
    project_id: UUID, release_id: UUID, document_id: UUID = None
) -> List[ProductInsight]:
    if not is_valid_uuid(project_id) or (not does_project_exist(project_id)):
        raise ValueError(f"No project found with document_id {project_id}")
    if not is_valid_uuid(release_id) or (not does_release_exist(release_id)):
        raise ValueError(f"No release found with document_id {release_id}")
    if document_id and (
        (not is_valid_uuid(document_id)) or (not does_document_exist(document_id))
    ):
        raise ValueError(f"No document found with document_id {document_id}")

    if document_id:
        query_data = (str(project_id), str(release_id), str(document_id))
        query = """SELECT id, status, details from product_insight
            WHERE deleted_at is null AND project_id = ? AND release_id = ? AND document_id = ?"""
    else:
        query_data = (str(project_id), str(release_id))
        query = """SELECT id, status, details from product_insight
            WHERE deleted_at is null AND project_id = ? AND release_id = ?"""

    with sqlite3.connect(config.RELATIONAL_DB_NAME) as conn:
        result = conn.execute(query, query_data).fetchall()

    return [
        {"id": insight[0], "status": insight[1], "details": insight[2]}
        for insight in result
    ]


def get_insight(insight_id: UUID) -> Dict | None:

    if not is_valid_uuid(insight_id):
        raise ValueError("insight_id should be valid_uuid")

    with sqlite3.connect(config.RELATIONAL_DB_NAME) as conn:
        result = conn.execute(
            """SELECT id, project_id, release_id, document_id, status, details FROM product_insight
            WHERE id = ? and deleted_at is null""",
            (str(insight_id),),
        ).fetchone()

    if not result:
        return None

    return {
        "id": result[0],
        "project_id": result[1],
        "release_id": result[2],
        "document_id": result[3],
        "status": result[4],
        "details": json.loads(result[5]),
    }


def update_insight(insight_id: UUID, insight_patch: Dict):
    existing_insight = get_insight(insight_id)
    if not existing_insight:
        raise ValueError(f"No insight found with id '{insight_id}'")

    existing_insight["details"].update(insight_patch)

    updates = ["details = ?"]
    values = [json.dumps(existing_insight["details"])]
    if insight_patch.get("status", None):
        updates.append("status = ?")
        values.append(insight_patch["status"])
    values.append(str(insight_id))
    with sqlite3.connect(config.RELATIONAL_DB_NAME) as conn:
        conn.execute(
            f"""UPDATE product_insight 
            SET modified_at = CURRENT_TIMESTAMP, 
            {" , ".join(updates)} 
            WHERE id = ?""",
            tuple(values),
        )


def create_concerns(
    project_id: UUID,
    release_id: UUID,
    document_id: UUID,
    product_concerns: List[ProductConcern],
) -> List[UUID]:

    data = [
        (
            str(concern.id),
            str(project_id),
            str(release_id),
            str(document_id),
            concern.status,
            concern.model_dump_json(),
        )
        for concern in product_concerns
    ]
    with sqlite3.connect(config.RELATIONAL_DB_NAME) as conn:

        conn.executemany(
            """INSERT OR REPLACE INTO product_concern
            (id, project_id, release_id, document_id, status, details) VALUES (?,?,?,?,?,?)""",
            data,
        )
    return [concern.id for concern in product_concerns]


def get_concerns(
    project_id: UUID, release_id: UUID, document_id: UUID = None
) -> List[ProductInsight]:

    if not is_valid_uuid(project_id) or (not does_project_exist(project_id)):
        raise ValueError(f"No project found with document_id {project_id}")
    if not is_valid_uuid(release_id) or (not does_release_exist(release_id)):
        raise ValueError(f"No release found with document_id {release_id}")
    if document_id and (
        (not is_valid_uuid(document_id)) or (not does_document_exist(document_id))
    ):
        raise ValueError(f"No document found with document_id {document_id}")

    if document_id:
        query_data = (str(project_id), str(release_id), str(document_id))
        query = """SELECT id, status, details from product_concern
            WHERE deleted_at is null AND project_id = ? AND release_id = ? AND document_id = ?"""
    else:
        query_data = (str(project_id), str(release_id))
        query = """SELECT id, status, details from product_concern
            WHERE deleted_at is null AND project_id = ? AND release_id = ?"""

    with sqlite3.connect(config.RELATIONAL_DB_NAME) as conn:
        result = conn.execute(query, query_data).fetchall()

    return [
        {"id": concern[0], "status": concern[1], "details": concern[2]}
        for concern in result
    ]


def get_concern(concern_id: UUID) -> Dict | None:

    if not is_valid_uuid(concern_id):
        raise ValueError("concern_id should be valid_uuid")

    with sqlite3.connect(config.RELATIONAL_DB_NAME) as conn:
        result = conn.execute(
            """SELECT id, project_id, release_id, document_id, status, details, resolved_by FROM product_concern
            WHERE id = ? and deleted_at is null""",
            (str(concern_id),),
        ).fetchone()

    if not result:
        return None

    return {
        "id": result[0],
        "project_id": result[1],
        "release_id": result[2],
        "document_id": result[3],
        "status": result[4],
        "details": json.loads(result[5]),
        "resolved_by": result[6],
    }


def update_concern(concern_id: UUID, concern_patch: Dict):
    existing_insight = get_concern(concern_id)
    if not existing_insight:
        raise ValueError(f"No insight found with id '{concern_id}'")

    existing_insight["details"].update(concern_patch)

    updates = ["details = ?"]
    values = [json.dumps(existing_insight["details"])]
    if concern_patch.get("status", None):
        updates.append("status = ?")
        values.append(concern_patch["status"])
    values.append(str(concern_id))
    with sqlite3.connect(config.RELATIONAL_DB_NAME) as conn:
        conn.execute(
            f"""UPDATE product_concern
            SET modified_at = CURRENT_TIMESTAMP, 
            {" , ".join(updates)} 
            WHERE id = ?""",
            tuple(values),
        )
