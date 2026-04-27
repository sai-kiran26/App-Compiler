from __future__ import annotations

from models import (
    BusinessRule,
    DesignSpec,
    EntitySpec,
    FieldSpec,
    FlowSpec,
    PageSpec,
    RoleSpec,
)


def _entity_fields(name: str) -> list[FieldSpec]:
    base_fields = [
        FieldSpec(name="id", type="uuid", required=True, unique=True),
        FieldSpec(name="created_at", type="timestamp", required=True),
    ]
    if name == "contact":
        return base_fields + [
            FieldSpec(name="name", type="string"),
            FieldSpec(name="email", type="string"),
            FieldSpec(name="phone", type="string", required=False),
            FieldSpec(name="company", type="string", required=False),
        ]
    if name == "lead":
        return base_fields + [
            FieldSpec(name="name", type="string"),
            FieldSpec(name="stage", type="string"),
            FieldSpec(name="value", type="number", required=False),
        ]
    if name == "ticket":
        return base_fields + [
            FieldSpec(name="title", type="string"),
            FieldSpec(name="status", type="string"),
            FieldSpec(name="priority", type="string", required=False),
        ]
    if name == "subscription":
        return base_fields + [
            FieldSpec(name="user_id", type="uuid"),
            FieldSpec(name="plan", type="string"),
            FieldSpec(name="status", type="string"),
        ]
    if name == "payment":
        return base_fields + [
            FieldSpec(name="user_id", type="uuid"),
            FieldSpec(name="amount", type="number"),
            FieldSpec(name="currency", type="string"),
        ]
    if name == "event":
        return base_fields + [
            FieldSpec(name="name", type="string"),
            FieldSpec(name="value", type="number", required=False),
        ]
    if name == "user":
        return base_fields + [
            FieldSpec(name="email", type="string", unique=True),
            FieldSpec(name="password_hash", type="string"),
            FieldSpec(name="role", type="string"),
        ]
    return base_fields + [
        FieldSpec(name="name", type="string"),
        FieldSpec(name="description", type="string", required=False),
    ]


def _default_pages() -> list[PageSpec]:
    return [
        PageSpec(name="Login", route="/login", components=[], roles_allowed=[]),
        PageSpec(name="Dashboard", route="/", components=[], roles_allowed=["admin", "member"]),
    ]


def design_system(intent) -> DesignSpec:
    entities = [EntitySpec(name="user", fields=_entity_fields("user"))]
    for entity in intent.entities:
        entities.append(EntitySpec(name=entity, fields=_entity_fields(entity)))

    if intent.payments:
        entities.append(EntitySpec(name="subscription", fields=_entity_fields("subscription")))
        entities.append(EntitySpec(name="payment", fields=_entity_fields("payment")))

    if intent.analytics:
        entities.append(EntitySpec(name="event", fields=_entity_fields("event")))

    roles = [RoleSpec(name=role, permissions=[]) for role in intent.roles]

    pages = _default_pages()
    for entity in intent.entities:
        pages.append(
            PageSpec(
                name=f"{entity.title()}s",
                route=f"/{entity}s",
                components=[],
                roles_allowed=["admin", "member"],
            )
        )

    if intent.analytics:
        pages.append(
            PageSpec(
                name="Analytics",
                route="/analytics",
                components=[],
                roles_allowed=["admin"],
            )
        )

    if intent.payments:
        pages.append(
            PageSpec(
                name="Billing",
                route="/billing",
                components=[],
                roles_allowed=["admin", "member"],
            )
        )

    flows = [
        FlowSpec(
            name="user_login",
            steps=["enter_credentials", "verify", "issue_session"],
        )
    ]

    rules = []
    if intent.payments:
        rules.append(
            BusinessRule(
                name="premium_gating",
                condition="plan != 'premium'",
                effect="deny_access_to_premium_features",
            )
        )

    return DesignSpec(
        entities=entities,
        pages=pages,
        roles=roles,
        flows=flows,
        business_rules=rules,
    )
