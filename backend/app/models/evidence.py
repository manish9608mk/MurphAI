from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from backend.app.database.database import Base


class Evidence(Base):
    """
    Stores proof that work was actually performed.

    Relationship:

        Job
         ↓
      Assignment
         ↓
        Work
         ↓
      Evidence

    Example:

        Work #3
        "Electrical wiring completed"
              ↓
        Evidence #1
        type = "photo"
        url = "https://example.com/photo.jpg"
    """

    __tablename__ = "evidence"

    # --------------------------------------------------------
    # Primary Key
    # --------------------------------------------------------

    # Unique ID for this evidence record.
    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # --------------------------------------------------------
    # Work Relationship
    # --------------------------------------------------------

    # Every evidence record belongs to one Work record.
    #
    # We connect Evidence to Work instead of directly
    # connecting it to Job or Worker.
    work_id = Column(
        Integer,
        ForeignKey("works.id"),
        nullable=False,
        index=True,
    )

    # --------------------------------------------------------
    # Evidence Type
    # --------------------------------------------------------

    # Type of proof.
    #
    # Examples:
    #     photo
    #     document
    #     video
    #     receipt
    #     other
    evidence_type = Column(
        String(30),
        nullable=False,
    )

    # --------------------------------------------------------
    # Evidence Location
    # --------------------------------------------------------

    # URL or storage path where the evidence is stored.
    #
    # In the future this can point to:
    #     AWS S3
    #     Cloud storage
    #     CDN
    #
    # For now we simply store the location.
    url = Column(
        String(2000),
        nullable=False,
    )

    # --------------------------------------------------------
    # Description
    # --------------------------------------------------------

    # Optional explanation about the evidence.
    #
    # Example:
    # "Photo showing the replaced electrical panel."
    description = Column(
        String(2000),
        nullable=True,
    )

    # --------------------------------------------------------
    # Timestamp
    # --------------------------------------------------------

    # When this evidence was uploaded/registered.
    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )