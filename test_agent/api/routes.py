from fastapi import FastAPI, BackgroundTasks
import base64
from uuid import UUID

from test_agent.services.document_service import ingest_document
from test_agent.services.product_service import generate_insights
from test_agent.db.repositories.core import (
    get_organizations,
    get_projects,
    get_releases,
    create_organization,
    create_project,
    create_release,
)
from test_agent.db.repositories.document import get_documents_by_release, does_document_exist
from test_agent.schemas.api_schemas.core import (
    CreateOrganizationRequest,
    CreateProjectRequest,
    CreateReleaseRequest,
    ResourceCreationResponse,
    ResourceType,
)
from test_agent.schemas.api_schemas.document import (
    IngestDocumentRequest,
    IngestDocumentResponse,
)
from test_agent.schemas.api_schemas.product import (
    GenerateProductInsightsRequest,
    GenerateProductInsightsResponse,
)


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

@app.get("/documents")
def get_documents_endpoint(project_id: UUID, release_id: UUID):
    return [ {"id": doc["id"], "hash": doc["hash"]} for doc in get_documents_by_release(project_id, release_id)]

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
def upload_documents_endpoint(
    req_body: IngestDocumentRequest, background_tasks: BackgroundTasks
) -> IngestDocumentResponse:

    encoded_bytes = req_body.document.document_content_base64.encode("utf-8")
    doc_content_bytes = base64.b64decode(encoded_bytes, validate=True)

    background_tasks.add_task(
        ingest_document,
        project_id=req_body.project_id,
        release_id=req_body.release_id,
        document=doc_content_bytes,
        document_type=req_body.document.document_type,
        document_status=req_body.document.document_status,
    )
    return IngestDocumentResponse()


@app.post("/product/insights/generate")
def generate_insights_endpoint(
    req_body: GenerateProductInsightsRequest, backround_tasks: BackgroundTasks
) -> GenerateProductInsightsResponse:

    if not does_document_exist(req_body.document_id):
        return GenerateProductInsightsResponse(
            status="FAIL",
            message=f"No document found of document_id '{req_body.document_id}'"
        )
    backround_tasks.add_task(
        generate_insights,
        document_ids=[req_body.document_id],
        project_id=req_body.project_id,
        release_id=req_body.release_id,
    )
    return GenerateProductInsightsResponse(
        message=f"Product insights generation initiated for documents - [{req_body.document_id}]"
    )


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
