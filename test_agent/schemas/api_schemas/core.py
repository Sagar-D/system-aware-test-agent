from pydantic import BaseModel
from uuid import UUID
from enum import Enum
from typing import Dict
from test_agent.schemas.api_schemas.common import ReleaseStatus

class CreateOrganizationRequest(BaseModel) :
    name: str

class CreateProjectRequest(BaseModel) :
    org_id: UUID
    name: str

class CreateReleaseRequest(BaseModel) :
    project_id: UUID
    release_label: str
    release_status: ReleaseStatus

class ResourceType(str, Enum):
    ORGANIZATION = "ORGANIZATION"
    USER = "USER"
    PROJECT = "PROJECT"
    RELEASE = "RELEASE"

class TransactionStatus(str, Enum) :
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"

class ResourceCreationResponse(BaseModel) :
    status: TransactionStatus = TransactionStatus.SUCCESS
    resource_type: ResourceType
    resource_id: UUID
    metadata: Dict
