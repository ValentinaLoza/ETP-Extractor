from pydantic import BaseModel, Field


class AngularAnalysisReport(BaseModel):
    files_scanned: list[str] = Field(default_factory=list)
    api_routes: list[str] = Field(default_factory=list)
    keywords_found: dict[str, list[str]] = Field(default_factory=dict)
    possible_interceptors: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
