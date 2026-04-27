from __future__ import annotations

import re

from models import IntentSpec


DEFAULT_ROLES = ["admin", "member"]


def _has(text: str, keyword: str) -> bool:
    return keyword in text


def extract_intent(prompt: str) -> IntentSpec:
    lowered = prompt.lower()
    features = []
    entities = []
    constraints = []
    roles = []

    if _has(lowered, "crm"):
        features.append("crm")
    if _has(lowered, "login") or _has(lowered, "auth"):
        features.append("login")
    if _has(lowered, "dashboard"):
        features.append("dashboard")
    if _has(lowered, "role"):
        features.append("role_access")
    if _has(lowered, "payment") or _has(lowered, "premium"):
        features.append("payments")
    if _has(lowered, "analytics"):
        features.append("analytics")

    if _has(lowered, "contact"):
        entities.append("contact")
    if _has(lowered, "lead"):
        entities.append("lead")
    if _has(lowered, "ticket"):
        entities.append("ticket")

    if _has(lowered, "admin"):
        roles.append("admin")
    if _has(lowered, "user") or _has(lowered, "member"):
        roles.append("member")

    payments = "payments" in features
    analytics = "analytics" in features

    name_match = re.search(r"build a ([a-z0-9\- ]+)", lowered)
    if name_match:
        app_name = name_match.group(1).strip().title()
    elif "crm" in features:
        app_name = "CRM"
    else:
        app_name = "App"

    if not roles:
        roles = DEFAULT_ROLES
        constraints.append("default_roles_assumed")

    if not entities:
        if "crm" in features:
            entities.append("contact")
        else:
            entities.append("item")
        constraints.append("default_entity_assumed")

    return IntentSpec(
        app_name=app_name,
        features=sorted(set(features)),
        roles=sorted(set(roles)),
        entities=sorted(set(entities)),
        constraints=constraints,
        payments=payments,
        analytics=analytics,
    )
