from fastapi import FastAPI
from test_agent.schemas.api_schemas.document import IngestDocumentRequest, IngestDocumentResponse
from uuid import UUID
from test_agent.db.repositories.core import get_organizations, get_projects, get_releases, create_organization, create_project, create_release

app = FastAPI()


@app.get("/organizations")
def get_organizations_endpoint():
    return get_organizations()
    

@app.get("/projects")
def get_projects_endpoint(org_id:UUID):
    return get_projects(org_id)

@app.get("/releases")
def get_releases_endpoint(project_id: UUID):
    return get_releases(project_id)

@app.post("/organization")
def create_organization_endpoint(organization_name: str) :
    organization = create_organization(organization_name)
    return organization

@app.post("/project")
def create_project_endpoint(org_id: UUID, project_name: str) :
    project = create_project(org_id,project_name)
    return project

@app.post("/release")
def create_release_endpoint(project_id: UUID, release_label: str, release_status: str) :
    release = create_release(project_id, release_label, release_status)

# @app.post("/documents/upload")
# def upload_documents_endpoint(data: IngestDocumentRequest) -> IngestDocumentResponse:
#     pass

# @app.post("/product/insights/generate")
# def get_insights_endpoint() :
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
