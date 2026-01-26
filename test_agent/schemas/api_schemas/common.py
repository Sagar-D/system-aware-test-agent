from enum import Enum

class ReleaseStatus(str, Enum):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"