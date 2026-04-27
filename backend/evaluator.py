from __future__ import annotations

import time
from typing import Any, Dict, List

from pipeline.design import design_system
from pipeline.intent import extract_intent
from pipeline.schema import generate_schema
from pipeline.validator import ValidationEngine


REAL_PROMPTS = [
    "Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics.",
    "Create a task management app with teams, assignments, and a kanban board.",
    "Build a simple helpdesk with tickets, status workflow, and agent dashboard.",
    "Make a sales tracker with leads, pipeline stages, and monthly reports.",
    "Create an inventory system with items, suppliers, and low-stock alerts.",
    "Build a subscription SaaS with user roles, billing, and usage limits.",
    "Create a basic HR portal with employees, time off requests, and approvals.",
    "Make a lightweight analytics dashboard for marketing campaigns.",
    "Create a clinic booking system with appointments and reminders.",
    "Build a project tracker with milestones and file uploads.",
]

EDGE_PROMPTS = [
    "Build something cool.",
    "CRM but no database.",
    "Create an app with payments but without users.",
    "Make a dashboard that is both public and admin-only.",
    "Build a system with role-based access but no roles.",
    "Create a platform with infinite entities.",
    "Make a login flow without passwords.",
    "Design a chat app with real-time sync and offline-first.",
    "Build a CRM with contacts but also prohibit storing contacts.",
    "Create a premium plan with no billing integration.",
]


def _compile_prompt(prompt: str):
    intent = extract_intent(prompt)
    design = design_system(intent)
    bundle = generate_schema(design, prompt)
    validator = ValidationEngine(max_retries=2)
    validation_report = validator.validate_and_repair(bundle)
    return {
        "intent": intent,
        "design": design,
        "config": bundle,
        "validation": validation_report,
    }


def evaluate_prompts(prompts: List[str]) -> Dict[str, Any]:
    results = []
    total_retries = 0
    failures = 0
    start = time.time()

    for prompt in prompts:
        compile_start = time.time()
        result = _compile_prompt(prompt)
        duration = time.time() - compile_start
        issues = [issue.message for issue in result["validation"].issues]
        if not result["validation"].valid:
            failures += 1
        total_retries += result["validation"].retries
        results.append(
            {
                "prompt": prompt,
                "valid": result["validation"].valid,
                "retries": result["validation"].retries,
                "issues": issues,
                "latency_ms": int(duration * 1000),
            }
        )

    total_time = time.time() - start
    success_rate = (len(prompts) - failures) / max(len(prompts), 1)
    avg_retries = total_retries / max(len(prompts), 1)

    return {
        "count": len(prompts),
        "success_rate": round(success_rate, 2),
        "avg_retries": round(avg_retries, 2),
        "latency_ms": int(total_time * 1000),
        "results": results,
    }
