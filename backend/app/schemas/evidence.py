from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EvidenceCreate(BaseModel):
    """
    Data required to add proof to a Work record.
    """

    # Work that this evidence belongs to.
    work_id: int = Field(gt=0)

    # Type of evidence.
    # Example: photo, document, video, receipt.
    evidence_type: str = Field(
        default="photo",
        min_length=1,
        max_length=30,
    )

    # Optional explanation of the evidence.
    description: str | None = Field(
        default=None,
        max_length=2000,
    )

    # URL or storage location of the evidence.
    url: str = Field(
        min_length=1,
        max_length=2000,
    )


class EvidenceResponse(BaseModel):
    """
    Data returned to the API client.
    """

    id: int
    work_id: int
    evidence_type: str
    description: str | None
    url: str
    created_at: datetime

    # Allows Pydantic to read data directly
    # from the SQLAlchemy Evidence model.
    model_config = ConfigDict(from_attributes=True)