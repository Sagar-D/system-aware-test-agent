import sqlite3
from typing import List, Dict
from test_agent import config
from uuid6 import uuid7
from uuid import UUID


def is_valid_uuid(value):
    try:
        UUID(str(value))
        return True
    except ValueError:
        return False


def get_organizations() -> List[Dict]:

    with sqlite3.connect(config.RELATIONAL_DB_NAME) as conn:
        result = conn.execute(
            """SELECT * FROM organization WHERE deleted_at is null"""
        ).fetchall()

    return [{"id": row[0], "name": row[1]} for row in result]


def create_organization(name: str) -> List[Dict]:

    with sqlite3.connect(config.RELATIONAL_DB_NAME) as conn:
        result = conn.execute(
            """SELECT id FROM organization WHERE name = ? AND deleted_at is null""",
            (name,),
        ).fetchall()
        if result:
            raise ValueError(f"Organization with name '{name}' already exists.")

        org_id = uuid7()
        conn.execute(
            """INSERT INTO organization (id, name) VALUES (?,?)""", (str(org_id), name)
        )
    return {"id": org_id, "name": name}


def get_projects(organization_id: UUID) -> List[Dict]:

    if not is_valid_uuid(organization_id):
        raise ValueError(f"organization_id should be a valid UUID")

    with sqlite3.connect(config.RELATIONAL_DB_NAME) as conn:
        result = conn.execute(
            """SELECT * FROM project WHERE organization_id = ? AND deleted_at is null""",
            (str(organization_id),),
        ).fetchall()

    return [{"id": row[0], "organization_id": row[1], "name": row[2]} for row in result]


def create_project(organization_id: UUID, project_name: str) -> List[Dict]:

    if not is_valid_uuid(organization_id):
        raise ValueError(f"organization_id should be a valid UUID")

    with sqlite3.connect(config.RELATIONAL_DB_NAME) as conn:
        result = conn.execute(
            """SELECT project.name, project.id 
            FROM project INNER JOIN organization 
            WHERE project.organization_id = organization.id 
            AND organization.deleted_at is null 
            AND project.deleted_at is null 
            AND project.name = ? 
            AND organization.id = ?""",
            (project_name, str(organization_id)),
        ).fetchall()
        if result:
            raise ValueError(
                f"Project with name '{project_name}' already exists for organization '{organization_id}'."
            )

        project_id = uuid7()
        conn.execute(
            """INSERT INTO project (id, organization_id, name) VALUES (?,?,?)""",
            (str(project_id), str(organization_id), project_name),
        )

    return {
        "id": project_id,
        "organization_id": organization_id,
        "name": project_name,
    }


def get_releases(project_id: UUID) -> List[Dict]:

    if not is_valid_uuid(project_id):
        raise ValueError(f"project_id should be a valid UUID")

    with sqlite3.connect(config.RELATIONAL_DB_NAME) as conn:
        result = conn.execute(
            """SELECT * FROM release WHERE project_id = ? AND deleted_at is null""",
            (str(project_id),),
        ).fetchall()

    return [{"id": row[0], "project_id": row[1], "label": row[2]} for row in result]


def create_release(
    project_id: UUID, release_label: str, release_status: str
) -> List[Dict]:

    release_status = release_status.upper()
    if release_status not in config.RELEASE_STATUS_LIST:
        raise ValueError(f"release_status should be one of the value")
    if not is_valid_uuid(project_id):
        raise ValueError(f"project_id should be a valid UUID")

    with sqlite3.connect(config.RELATIONAL_DB_NAME) as conn:
        result = conn.execute(
            """SELECT release.label, release.id 
            FROM project INNER JOIN release 
            WHERE project.id = release.project_id 
            AND release.label = ? 
            AND project.id = ?
            AND project.deleted_at is null 
            AND release.deleted_at is null """,
            (
                release_label,
                str(project_id),
            ),
        ).fetchall()
        if result:
            raise ValueError(
                f"Release with label '{release_label}' already exists for project '{project_id}'."
            )

        release_id = uuid7()
        conn.execute(
            """INSERT INTO release (id, project_id, label, status) VALUES (?,?,?,?)""",
            (str(release_id), str(project_id), release_label, release_status),
        )

    return {
        "id": release_id,
        "organization_id": project_id,
        "label": release_label,
    }
