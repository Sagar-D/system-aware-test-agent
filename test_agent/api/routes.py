from fastapi import FastAPI
import base64
from test_agent.schemas.api_schemas.document import (
    IngestDocumentRequest,
    IngestDocumentResponse,
)
from test_agent.document.document_processor import get_processed_document, chunk_markdown_document
from test_agent.schemas.api_schemas.core import (
    CreateOrganizationRequest,
    CreateProjectRequest,
    CreateReleaseRequest,
    ResourceCreationResponse,
    ResourceType,
)
from uuid import UUID
from test_agent.db.repositories.core import (
    get_organizations,
    get_projects,
    get_releases,
    create_organization,
    create_project,
    create_release,
)
from test_agent.db.repositories.document import store_document, store_document_chunks

app = FastAPI()


@app.get("/organizations")
def get_organizations_endpoint():
    return get_organizations()


@app.get("/projects")
def get_projects_endpoint(org_id: UUID):
    return get_projects(org_id)


@app.get("/releases")
def get_releases_endpoint(project_id: UUID):
    return get_releases(project_id)


@app.post("/organization")
def create_organization_endpoint(
    org: CreateOrganizationRequest,
) -> ResourceCreationResponse:
    organization = create_organization(org.name)
    return ResourceCreationResponse(
        resource_type=ResourceType.ORGANIZATION,
        resource_id=organization["id"],
        metadata=organization,
    )


@app.post("/project")
def create_project_endpoint(project: CreateProjectRequest) -> ResourceCreationResponse:
    project = create_project(project.org_id, project.name)
    return ResourceCreationResponse(
        resource_type=ResourceType.PROJECT, resource_id=project["id"], metadata=project
    )


@app.post("/release")
def create_release_endpoint(release: CreateReleaseRequest) -> ResourceCreationResponse:
    release = create_release(
        release.project_id, release.release_label, release.release_status
    )
    return ResourceCreationResponse(
        resource_type=ResourceType.RELEASE, resource_id=release["id"], metadata=release
    )


@app.post("/document/upload")
def upload_documents_endpoint(reqBody: IngestDocumentRequest) -> IngestDocumentResponse:
    
    encoded_bytes = reqBody.document.document_content_base64.encode("utf-8")
    doc_content_bytes = base64.b64decode(encoded_bytes, validate=True)
    doc_hash, doc_content_markdown = get_processed_document(doc_content_bytes)
    document_id = store_document(
        project_id=reqBody.project_id,
        document_type=reqBody.document.document_type,
        content=doc_content_markdown,
        document_hash=doc_hash,
        document_status=reqBody.document.document_status,
        release_id=reqBody.release_id,
    )
    chunks = [chunk.page_content for chunk in chunk_markdown_document(doc_content_markdown)]
    store_document_chunks(document_id, chunks)
    return IngestDocumentResponse(status="SUCCESS", document_id=document_id, document_hash=doc_hash)


# @app.post("/product/insights/generate")
# def generate_insights_endpoint() :
#     pass

# @app.get("product/insights")
# def get_insights_endpoint() :
#     pass

# @app.get("product/concerns")
# def get_concerns_endpoint() :
#     pass

# @app.post("product/insights")
# def create_insights_endpoint() :
#     pass

# @app.post("product/concerns")
# def create_concerns_endpoint() :
#     pass

# @app.put("product/insights")
# def update_insights_endpoint() :
#     pass

# @app.put("product/concerns")
# def update_concerns_endpoint() :
#     pass
