import sqlite3
from uuid import UUID
from uuid6 import uuid7
from test_agent import config
from test_agent.db.repositories.core import (
    get_releases,
    does_release_exist,
    does_project_exist,
)
from test_agent.utils.common import is_valid_uuid


def store_document(
    project_id: UUID,
    document_type: str,
    content: str,
    document_hash: str,
    document_status: str,
    release_id: UUID = None,
) -> UUID:

    document_type = document_type.upper()
    if document_type not in config.DOCUMENT_TYPES:
        raise ValueError(
            f"Not supported document type - {document_type}. Should be one of - {", ".join(config.DOCUMENT_TYPES)}"
        )
    document_status = document_status.upper()
    if document_status not in config.RELEASE_STATUS_LIST:
        raise ValueError(
            f"Not supported document type - {document_status}. Should be one of - {", ".join(config.RELEASE_STATUS_LIST)}"
        )
    if not does_project_exist(project_id):
        raise ValueError(f"Project Not Found: project_id - {project_id}")
    if not release_id:
        releases = get_releases(project_id)
        if not releases:
            raise ValueError(
                f"No release found for the project '{project_id}'. Please create a release before moving ahead."
            )
        release_id = releases[-1]["id"]
    elif not does_release_exist(release_id):
        raise ValueError(f"Release Not Found: release_id - {release_id}")

    with sqlite3.connect(config.RELATIONAL_DB_NAME) as conn:

        result = conn.execute(
            """SELECT id from document 
            WHERE document_hash = ? AND project_id = ? AND release_id = ? ORDER BY created_at DESC""",
            (str(document_hash), str(project_id), str(release_id)),
        ).fetchone()

        if result:
            return result[0]

        document_id = uuid7()
        conn.execute(
            """INSERT INTO document (id, project_id, release_id, document_type, status, content, document_hash)
            VALUES (?,?,?,?,?,?,?)""",
            (
                str(document_id),
                str(project_id),
                str(release_id),
                document_type,
                document_status,
                content,
                str(document_hash),
            ),
        )
    return document_id


def does_document_exist(document_id) -> bool:
    if not is_valid_uuid(document_id):
        raise ValueError("Document Id should be a valid UUID")
    with sqlite3.connect(config.RELATIONAL_DB_NAME) as conn:
        result = conn.execute(
            """SELECT * from document where id = ?""", (str(document_id),)
        )
    if result:
        return True
    return False


def store_document_chunks(
    document_id: UUID, chunks: list[str]
) -> UUID:
    
    if not does_document_exist(document_id):
        raise ValueError(f"Document Not Found: document_id - {document_id}")
    
    chunk_ids = []
    for index, chunk_content in enumerate(chunks):

        with sqlite3.connect(config.RELATIONAL_DB_NAME) as conn:

            chunk_id = uuid7()
            result = conn.execute(
                """SELECT * from document_chunk 
                WHERE document_id = ? AND chunk_index = ?""",
                (
                    str(document_id),
                    index,
                ),
            ).fetchone()
            if result:
                chunk_id = result[0]

            conn.execute(
                """INSERT OR REPLACE INTO document_chunk (id, document_id, chunk_index, content)
                VALUES (?,?,?,?)""",
                (
                    str(chunk_id),
                    str(document_id),
                    index,
                    chunk_content,
                ),
            )
            chunk_ids.append(chunk_id)
    return chunk_ids
