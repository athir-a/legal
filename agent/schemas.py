from pydantic import BaseModel, Field


class Citation(BaseModel):
    act: str
    section: str
    page: int | None = None
    source: str | None = None


class LegalAnswer(BaseModel):
    answer: str
    supported: bool
    citations: list[Citation] = Field(default_factory=list)