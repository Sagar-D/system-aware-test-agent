from pydantic import BaseModel
from uuid import UUID
from enum import Enum
from test_agent.schemas.api_schemas.common import ReleaseStatus


class DocumentType(str, Enum):
    PRD = "PRD"
    ADR = "ADR"
    DB_SCHEMA = "DB_SCHEMA"
    API_SPEC = "API_SPEC"
    OTHER = "OTHER"


class Document(BaseModel):
    class Config:
        extra = "forbid"

    document_type: DocumentType
    document_content_base64: str
    document_name: str = None
    document_status: ReleaseStatus = ReleaseStatus.APPROVED


class IngestDocumentRequest(BaseModel):
    class Config:
        extra = "forbid"

    project_id: UUID
    release_id: UUID
    document: Document


class IngestDocumentResponse(BaseModel):
    class Config:
        extra = "forbid"

    status: str = "INITIATED"
    message: str = "Document Ingestion is initiated"
