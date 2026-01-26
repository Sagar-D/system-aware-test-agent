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
    document_type: DocumentType
    document_content_base64: str
    document_name: str = None
    document_status: ReleaseStatus = ReleaseStatus.APPROVED


class IngestDocumentRequest(BaseModel):
    project_id: UUID
    release_id: UUID
    document: Document

class IngestDocumentResponse(BaseModel):
    status: str
    document_id: UUID
    document_hash: str
