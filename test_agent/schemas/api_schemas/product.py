from pydantic import BaseModel
from uuid import UUID

class GenerateProductInsightsRequest(BaseModel):
    project_id: UUID
    release_id: UUID
    document_id: UUID

class GenerateProductInsightsResponse(BaseModel):
    status: str = "INITIATED"
    message: str = "Product Insights generation is initiated"