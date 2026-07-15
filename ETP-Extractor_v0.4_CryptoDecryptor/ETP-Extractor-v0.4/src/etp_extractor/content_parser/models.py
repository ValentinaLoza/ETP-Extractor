from pydantic import BaseModel, Field


class IPCItem(BaseModel):
    ata: str | None = None
    figure: str | None = None
    item_number: str | None = None
    description: str
    part_number: str | None = None
    quantity: str | None = None
    effectivity: str | None = None
    source_reference: str | None = None


class ParsedDocument(BaseModel):
    title: str | None = None
    document_id: str | None = None
    items: list[IPCItem] = Field(default_factory=list)
