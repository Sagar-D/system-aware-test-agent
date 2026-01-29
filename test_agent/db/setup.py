import sqlite3
from test_agent import config

default_organizations = [("d6573910-6b0f-4489-8ce1-c948c28bc42b", "Demo Organization")]

default_users = [
    (
        "85799544-6437-491a-858b-342fc3ec0992",
        "d6573910-6b0f-4489-8ce1-c948c28bc42b",
        "user",
        config.USER_ROLES[0],
        "password",
    ),
]

default_projects = [
    (
        "f221f079-267b-4070-bae4-89ccba8e5ac1",
        "d6573910-6b0f-4489-8ce1-c948c28bc42b",
        "Demo Project",
    ),
]

default_releases = [
    (
        "f7c4b578-b088-4c82-8ddb-64818f0038f1",
        "f221f079-267b-4070-bae4-89ccba8e5ac1",
        "v0.0.1",
        config.RELEASE_STATUS_LIST[-1],
    ),
]


def initialize_db():

    with sqlite3.connect(str(config.RELATIONAL_DB_NAME)) as conn:
        conn: sqlite3.Connection

        cursor = conn.cursor()

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS organization(
            id UUID PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            modified_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            deleted_at DATETIME DEFAULT NULL
            )
            """
        )

        cursor.executemany(
            """INSERT OR IGNORE INTO organization (id, name) VALUES ( ?, ?)""",
            default_organizations,
        )

        cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS user(
            id UUID PRIMARY KEY,
            organization_id UUID NOT NULL,
            name TEXT NOT NULL,
            role TEXT CHECK(role IN ({", ".join([f"'{role}'" for role in config.USER_ROLES])})) NOT NULL,
            password_hash TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            modified_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            deleted_at DATETIME DEFAULT NULL,
            FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE
            )
            """
        )

        cursor.executemany(
            """INSERT OR IGNORE INTO user (id, organization_id, name, role, password_hash) VALUES (?, ?, ?, ?, ?)""",
            default_users,
        )

        cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS project(
            id UUID PRIMARY KEY,
            organization_id UUID NOT NULL,
            name TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            modified_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            deleted_at DATETIME DEFAULT NULL,
            FOREIGN KEY (organization_id) REFERENCES organization(id) ON DELETE CASCADE,
            UNIQUE (organization_id, name)
            )
            """
        )

        cursor.executemany(
            """INSERT OR IGNORE INTO project (id, organization_id, name) VALUES (?, ?, ?)""",
            default_projects,
        )

        cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS release(
            id UUID PRIMARY KEY,
            project_id UUID NOT NULL,
            label TEXT NOT NULL,
            status TEXT CHECK(status IN ({", ".join([f"'{status}'" for status in config.RELEASE_STATUS_LIST])})) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            locked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            deleted_at DATETIME DEFAULT NULL,
            FOREIGN KEY (project_id) REFERENCES project(id) ON DELETE CASCADE,
            UNIQUE (project_id, label)
            )
            """
        )

        cursor.executemany(
            """INSERT OR IGNORE INTO release (id, project_id, label, status) VALUES (?, ?, ?, ?)""",
            default_releases,
        )

        cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS document(
            id UUID PRIMARY KEY,
            project_id UUID NOT NULL,
            release_id UUID NOT NULL,
            document_type TEXT CHECK(document_type IN ({", ".join([f"'{type}'" for type in config.DOCUMENT_TYPES])})) NOT NULL,
            status TEXT CHECK(status IN ({", ".join([f"'{status}'" for status in config.RELEASE_STATUS_LIST])})) NOT NULL,
            content TEXT NOT NULL,
            document_hash TEXT DEFAUL NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            deleted_at DATETIME DEFAULT NULL,
            locked_at DATETIME DEFAULT NULL,
            locked_by UUID DEFAULT NULL,
            FOREIGN KEY (project_id) REFERENCES project(id) ON DELETE CASCADE,
            FOREIGN KEY (release_id) REFERENCES release(id) ON DELETE CASCADE,
            FOREIGN KEY (locked_by) REFERENCES user(id)
            )
            """
        )

        cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS document_chunk(
            id UUID PRIMARY KEY,
            document_id UUID NOT NULL,
            chunk_index INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            deleted_at DATETIME DEFAULT NULL,
            FOREIGN KEY (document_id) REFERENCES document(id) ON DELETE CASCADE
            )
            """
        )

        cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS product_insight(
            id UUID PRIMARY KEY,
            project_id UUID NOT NULL,
            release_id UUID NOT NULL,
            document_id UUID NOT NULL,
            status TEXT CHECK(status IN ({", ".join([f"'{status}'" for status in config.INSIGHT_STATUS])})) NOT NULL,
            details JSONB CHECK(json_valid(details)) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            modified_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            deleted_at DATETIME DEFAULT NULL,
            FOREIGN KEY (project_id) REFERENCES project(id) ON DELETE CASCADE,
            FOREIGN KEY (release_id) REFERENCES release(id) ON DELETE CASCADE,
            FOREIGN KEY (document_id) REFERENCES document(id) ON DELETE CASCADE,
            FOREIGN KEY (resolved_by) REFERENCES user(id)
            )
            """
        )

        cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS product_concern(
            id UUID PRIMARY KEY,
            project_id UUID NOT NULL,
            release_id UUID NOT NULL,
            document_id UUID NOT NULL,
            status TEXT CHECK(status IN ({", ".join([f"'{status}'" for status in config.CONCERN_STATUS])})) NOT NULL,
            details JSONB NOT NULL,
            resolved_by UUID DEFAULT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            modified_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            deleted_at DATETIME DEFAULT NULL,
            FOREIGN KEY (project_id) REFERENCES project(id) ON DELETE CASCADE,
            FOREIGN KEY (release_id) REFERENCES release(id) ON DELETE CASCADE,
            FOREIGN KEY (document_id) REFERENCES document(id) ON DELETE CASCADE,
            FOREIGN KEY (resolved_by) REFERENCES user(id)
            )
            """
        )

        cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS product_concern_insights(
            concern_id UUID NOT NULL,
            insight_id UUID NOT NULL,
            PRIMARY KEY (concern_id, insight_id)
            FOREIGN KEY (concern_id) REFERENCES concern(id) ON DELETE CASCADE,
            FOREIGN KEY (insight_id) REFERENCES insight(id) ON DELETE CASCADE
            )
            """
        )


if __name__ == "__main__":
    initialize_db()
