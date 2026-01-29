from fastapi import FastAPI, BackgroundTasks
import base64
from uuid import UUID
from uuid6 import uuid7
from typing import List

from test_agent.services.document_service import ingest_document
from test_agent.services.product_service import (
    generate_insights,
    create_insights,
    create_concerns,
)
from test_agent.db.repositories.core import (
    get_organizations,
    get_projects,
    get_releases,
    create_organization,
    create_project,
    create_release,
)
from test_agent.db.repositories.document import (
    get_documents_by_release,
    does_document_exist,
)
from test_agent.db.repositories.product import (
    get_insights,
    get_concerns,
    update_insight,
    update_concern,
)
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
    ProductInsightGenerationStatus,
    CreateProductInsightRequest,
    CreateProductConcernRequest,
    ProductInsightUpdate,
    ProductConcernUpdate,
)
from test_agent.schemas.agent_schemas.prd_agent_schemas import (
    ProductInsight,
    ProductConcern,
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
    return [
        {"id": doc["id"], "hash": doc["hash"]}
        for doc in get_documents_by_release(project_id, release_id)
    ]


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
) -> List[GenerateProductInsightsResponse]:

    response = []
    filtered_document_ids = []
    for document_id in req_body.document_ids:
        if does_document_exist(document_id, req_body.project_id, req_body.release_id):
            response.append(
                GenerateProductInsightsResponse(
                    document_id=document_id,
                    status=ProductInsightGenerationStatus.INITIATED,
                    message="Product insight generation initiated.",
                )
            )
            filtered_document_ids.append(document_id)
        else:
            response.append(
                GenerateProductInsightsResponse(
                    document_id=document_id,
                    status=ProductInsightGenerationStatus.FAILED,
                    message=f"Document with id '{document_id}' does not exist in povided (project + release)",
                )
            )

    backround_tasks.add_task(
        generate_insights,
        document_ids=filtered_document_ids,
        project_id=req_body.project_id,
        release_id=req_body.release_id,
    )
    ## Create entry in  job_status table with status as INITIATED for all filtered_document_ids

    return response


@app.get("/product/insights")
def get_insights_endpoint(project_id: UUID, release_id: UUID, document_id: UUID = None):
    return get_insights(project_id, release_id, document_id)


@app.get("/product/concerns")
def get_concerns_endpoint(project_id: UUID, release_id: UUID, document_id: UUID = None):
    return get_concerns(project_id, release_id, document_id)


@app.post("/product/insights")
def create_insights_endpoint(req_body: CreateProductInsightRequest):
    product_insights = [
        ProductInsight(
            id=uuid7(),
            title=insight.title,
            description=insight.description,
            flow_type=insight.flow_type,
            priority=insight.priority,
            actors=insight.actors,
            inputs=insight.inputs,
            expected_outcomes=insight.expected_outcomes,
            preconditions=insight.preconditions,
            postconditions=insight.postconditions,
            business_rules=insight.business_rules,
            assumptions=insight.assumptions,
            non_goals=insight.non_goals,
            source_document=insight.source_document or req_body.document_id,
            status=insight.status,
            confidence_level=insight.confidence_level,
        )
        for insight in req_body.insights
    ]

    insight_ids = create_insights(
        project_id=req_body.project_id,
        release_id=req_body.release_id,
        document_id=req_body.document_id,
        product_insights=product_insights,
    )
    return {"insight_ids": insight_ids}


@app.post("/product/concerns")
def create_concerns_endpoint(req_body: CreateProductConcernRequest):
    product_concerns = [
        ProductConcern(
            id=uuid7(),
            related_product_insight_id=concern.related_product_insight_id,
            type=concern.type,
            severity=concern.severity,
            description=concern.description,
            impact=concern.impact,
            questions=concern.questions,
            raised_by=concern.raised_by,
            status=concern.status,
            source_document=concern.source_document,
        )
        for concern in req_body.concerns
    ]

    concern_ids = create_concerns(
        project_id=req_body.project_id,
        release_id=req_body.release_id,
        document_id=req_body.document_id,
        product_concerns=product_concerns,
    )
    return {"concern_ids": concern_ids}


@app.patch("/product/insight/{insight_id}")
def update_insights_endpoint(insight_id: UUID, insight: ProductInsightUpdate):
    update_insight(insight_id, insight.model_dump(exclude_unset=True))
    return {"status": "SUCCESS"}


@app.patch("/product/concern/{concern_id}")
def update_concerns_endpoint(concern_id: UUID, concern: ProductConcernUpdate):
    update_concern(concern_id, concern.model_dump(exclude_unset=True))
    return {"status": "SUCCESS"}
