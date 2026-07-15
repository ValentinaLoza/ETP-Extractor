from pydantic import BaseModel, Field


class Evidence(BaseModel):
    file: str
    offset: int
    snippet: str


class RouteFinding(BaseModel):
    route: str
    methods: list[str] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)


class TokenFlow(BaseModel):
    query_parameter: str | None = None
    interceptor_found: bool = False
    electron_get_channel: str | None = None
    electron_set_channel: str | None = None
    electron_callback_channel: str | None = None
    storage: str | None = None
    evidence: list[Evidence] = Field(default_factory=list)


class AngularAnalysisReport(BaseModel):
    files_scanned: list[str] = Field(default_factory=list)
    routes: list[RouteFinding] = Field(default_factory=list)
    token_flow: TokenFlow = Field(default_factory=TokenFlow)
    keywords_found: dict[str, list[str]] = Field(default_factory=dict)
    possible_interceptors: list[Evidence] = Field(default_factory=list)
    ipc_findings: list[Evidence] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
