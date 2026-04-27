from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class FieldSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    type: str
    required: bool = True
    unique: bool = False


class EntitySpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    fields: List[FieldSpec]


class RoleSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    permissions: List[str]


class ComponentSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str
    props: Dict[str, str] = Field(default_factory=dict)
    bindings: List[str] = Field(default_factory=list)


class PageSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    route: str
    components: List[ComponentSpec]
    roles_allowed: List[str] = Field(default_factory=list)


class UISchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pages: List[PageSpec]


class EndpointSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    method: str
    path: str
    entity: Optional[str] = None
    request_fields: List[str] = Field(default_factory=list)
    response_fields: List[str] = Field(default_factory=list)
    auth_required: bool = True
    roles_allowed: List[str] = Field(default_factory=list)


class APISchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    endpoints: List[EndpointSpec]


class RelationSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    from_table: str
    to_table: str
    type: str
    from_field: str
    to_field: str


class TableSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    columns: List[FieldSpec]


class DBSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tables: List[TableSpec]
    relations: List[RelationSpec] = Field(default_factory=list)


class AuthRule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: str
    allow: List[str]


class AuthSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    roles: List[RoleSpec]
    rules: List[AuthRule]


class BusinessRule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    condition: str
    effect: str


class LogicSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rules: List[BusinessRule]


class Metadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: str
    generated_at: str
    deterministic_seed: str


class SchemaBundle(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ui: UISchema
    api: APISchema
    db: DBSchema
    auth: AuthSchema
    logic: LogicSchema
    metadata: Metadata


class IntentSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    app_name: str
    features: List[str]
    roles: List[str]
    entities: List[str]
    constraints: List[str]
    payments: bool
    analytics: bool


class FlowSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    steps: List[str]


class DesignSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entities: List[EntitySpec]
    pages: List[PageSpec]
    roles: List[RoleSpec]
    flows: List[FlowSpec]
    business_rules: List[BusinessRule]


class ValidationIssue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    severity: str
    message: str
    path: str


class ValidationReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    valid: bool
    issues: List[ValidationIssue]
    repairs: List[str]
    retries: int


class ExecutionReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    executed: bool
    tables_created: List[str]
    errors: List[str]


class CompileResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prompt: str
    intent: IntentSpec
    design: DesignSpec
    config: SchemaBundle
    validation: ValidationReport
    execution: ExecutionReport
    assumptions: List[str]
    clarifying_questions: List[str]
