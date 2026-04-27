from __future__ import annotations

from typing import List, Tuple

from models import SchemaBundle, ValidationIssue, ValidationReport


def _table_map(bundle: SchemaBundle) -> dict[str, set[str]]:
    return {table.name: {col.name for col in table.columns} for table in bundle.db.tables}


def validate_bundle(bundle: SchemaBundle) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []
    table_fields = _table_map(bundle)
    role_names = {role.name for role in bundle.auth.roles}

    for role in bundle.auth.roles:
        if role.name not in role_names:
            issues.append(
                ValidationIssue(
                    severity="error",
                    message=f"auth role {role.name} is undefined",
                    path="auth.roles",
                )
            )

    for rule in bundle.auth.rules:
        if rule.role not in role_names:
            issues.append(
                ValidationIssue(
                    severity="error",
                    message=f"auth rule role {rule.role} not declared",
                    path="auth.rules",
                )
            )

    for endpoint in bundle.api.endpoints:
        if endpoint.entity:
            if endpoint.entity not in table_fields:
                issues.append(
                    ValidationIssue(
                        severity="error",
                        message=f"missing table for entity {endpoint.entity}",
                        path=f"api.endpoints.{endpoint.name}",
                    )
                )
        if endpoint.roles_allowed:
            for role in endpoint.roles_allowed:
                if role not in role_names:
                    issues.append(
                        ValidationIssue(
                            severity="error",
                            message=f"endpoint role {role} not declared",
                            path=f"api.endpoints.{endpoint.name}",
                        )
                    )
            else:
                for field in endpoint.request_fields + endpoint.response_fields:
                    if field not in table_fields[endpoint.entity]:
                        issues.append(
                            ValidationIssue(
                                severity="error",
                                message=f"field {field} not in table {endpoint.entity}",
                                path=f"api.endpoints.{endpoint.name}",
                            )
                        )

    for page in bundle.ui.pages:
        for role in page.roles_allowed:
            if role not in role_names:
                issues.append(
                    ValidationIssue(
                        severity="error",
                        message=f"page role {role} not declared",
                        path=f"ui.pages.{page.route}",
                    )
                )
        for component in page.components:
            for binding in component.bindings:
                if "." not in binding:
                    issues.append(
                        ValidationIssue(
                            severity="error",
                            message=f"invalid binding {binding}",
                            path=f"ui.pages.{page.route}",
                        )
                    )
                    continue
                entity, field = binding.split(".", 1)
                if entity not in table_fields:
                    issues.append(
                        ValidationIssue(
                            severity="error",
                            message=f"binding entity {entity} not found",
                            path=f"ui.pages.{page.route}",
                        )
                    )
                elif field not in table_fields[entity]:
                    issues.append(
                        ValidationIssue(
                            severity="error",
                            message=f"binding field {field} not found in {entity}",
                            path=f"ui.pages.{page.route}",
                        )
                    )
                else:
                    api_fields = set()
                    for endpoint in bundle.api.endpoints:
                        if endpoint.entity == entity:
                            api_fields.update(endpoint.response_fields)
                            api_fields.update(endpoint.request_fields)
                    if field not in api_fields:
                        issues.append(
                            ValidationIssue(
                                severity="error",
                                message=f"binding field {field} not in api for {entity}",
                                path=f"ui.pages.{page.route}",
                            )
                        )

    return issues


def repair_bundle(bundle: SchemaBundle) -> Tuple[SchemaBundle, List[str]]:
    repairs: List[str] = []
    table_fields = _table_map(bundle)

    for endpoint in bundle.api.endpoints:
        if endpoint.entity and endpoint.entity in table_fields:
            fields = table_fields[endpoint.entity]
            for field in endpoint.request_fields + endpoint.response_fields:
                if field not in fields:
                    table = next((t for t in bundle.db.tables if t.name == endpoint.entity), None)
                    if table:
                        table.columns.append(
                            type(table.columns[0])(
                                name=field,
                                type="string",
                                required=False,
                                unique=False,
                            )
                        )
                        repairs.append(f"added_field:{endpoint.entity}.{field}")
                        fields.add(field)

    table_fields = _table_map(bundle)

    for page in bundle.ui.pages:
        for component in page.components:
            fixed_bindings = []
            for binding in component.bindings:
                if "." not in binding:
                    continue
                entity, field = binding.split(".", 1)
                if entity in table_fields and field in table_fields[entity]:
                    fixed_bindings.append(binding)
                else:
                    repairs.append(f"removed_binding:{binding}")
            component.bindings = fixed_bindings

    return bundle, repairs


class ValidationEngine:
    def __init__(self, max_retries: int = 2) -> None:
        self.max_retries = max_retries

    def validate_and_repair(self, bundle: SchemaBundle) -> ValidationReport:
        retries = 0
        repairs = []
        issues = validate_bundle(bundle)

        while issues and retries < self.max_retries:
            bundle, new_repairs = repair_bundle(bundle)
            repairs.extend(new_repairs)
            retries += 1
            issues = validate_bundle(bundle)

        return ValidationReport(
            valid=not issues,
            issues=issues,
            repairs=repairs,
            retries=retries,
        )
