from __future__ import annotations

import datetime
import hashlib

from models import (
    APISchema,
    AuthRule,
    AuthSchema,
    BusinessRule,
    ComponentSpec,
    DBSchema,
    EndpointSpec,
    LogicSchema,
    Metadata,
    PageSpec,
    RelationSpec,
    SchemaBundle,
    TableSpec,
    UISchema,
)


def _deterministic_seed(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()


def _component_for_entity(entity: str) -> list[ComponentSpec]:
    return [
        ComponentSpec(type="table", props={"title": entity.title()}, bindings=[f"{entity}.id", f"{entity}.name"]),
        ComponentSpec(type="form", props={"entity": entity}, bindings=[f"{entity}.name"]),
    ]


def _endpoint_set(entity: str, roles: list[str]) -> list[EndpointSpec]:
    return [
        EndpointSpec(
            name=f"list_{entity}",
            method="GET",
            path=f"/api/{entity}s",
            entity=entity,
            response_fields=["id", "created_at", "name"],
            roles_allowed=roles,
        ),
        EndpointSpec(
            name=f"create_{entity}",
            method="POST",
            path=f"/api/{entity}s",
            entity=entity,
            request_fields=["name"],
            response_fields=["id", "created_at", "name"],
            roles_allowed=roles,
        ),
        EndpointSpec(
            name=f"get_{entity}",
            method="GET",
            path=f"/api/{entity}s/{entity}_id",
            entity=entity,
            response_fields=["id", "created_at", "name"],
            roles_allowed=roles,
        ),
    ]


def generate_schema(design, prompt: str) -> SchemaBundle:
    ui_pages = []
    for page in design.pages:
        components = []
        route_parts = page.route.strip("/").split("/")
        entity_guess = route_parts[0].rstrip("s") if route_parts[0] else ""
        if entity_guess:
            components = _component_for_entity(entity_guess)
        ui_pages.append(
            PageSpec(
                name=page.name,
                route=page.route,
                components=components,
                roles_allowed=page.roles_allowed,
            )
        )

    ui_schema = UISchema(pages=ui_pages)

    endpoints = [
        EndpointSpec(
            name="login",
            method="POST",
            path="/api/auth/login",
            request_fields=["email", "password"],
            response_fields=["token", "role"],
            auth_required=False,
            roles_allowed=[],
        )
    ]

    roles = sorted({role.name for role in design.roles})
    for entity in {entity.name for entity in design.entities}:
        endpoints.extend(_endpoint_set(entity, roles))

    api_schema = APISchema(endpoints=endpoints)

    tables = [TableSpec(name=entity.name, columns=entity.fields) for entity in design.entities]
    relations = []
    for entity in design.entities:
        if entity.name == "subscription":
            relations.append(
                RelationSpec(
                    from_table="subscription",
                    to_table="user",
                    type="many_to_one",
                    from_field="user_id",
                    to_field="id",
                )
            )
    db_schema = DBSchema(tables=tables, relations=relations)

    auth_rules = []
    for role in design.roles:
        auth_rules.append(AuthRule(role=role.name, allow=["*"]))

    auth_schema = AuthSchema(roles=design.roles, rules=auth_rules)

    logic_rules = [BusinessRule(name=rule.name, condition=rule.condition, effect=rule.effect) for rule in design.business_rules]
    logic_schema = LogicSchema(rules=logic_rules)

    metadata = Metadata(
        version="1.0",
        generated_at=datetime.datetime.utcnow().isoformat() + "Z",
        deterministic_seed=_deterministic_seed(prompt),
    )

    return SchemaBundle(
        ui=ui_schema,
        api=api_schema,
        db=db_schema,
        auth=auth_schema,
        logic=logic_schema,
        metadata=metadata,
    )
