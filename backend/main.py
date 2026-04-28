from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict

from evaluator import EDGE_PROMPTS, REAL_PROMPTS, evaluate_prompts
from execution import execute_schema
from models import CompileResult, SchemaBundle
from pipeline.design import design_system
from pipeline.intent import extract_intent
from pipeline.schema import generate_schema
from pipeline.validator import ValidationEngine, validate_bundle


class GenerateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prompt: str


class ValidateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    config: SchemaBundle


app = FastAPI(title="App Compiler", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path(__file__).resolve().parent / "data"
DB_PATH = DATA_DIR / "runtime.db"


def compile_prompt(prompt: str) -> CompileResult:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    intent = extract_intent(prompt)
    design = design_system(intent)
    bundle = generate_schema(design, prompt)
    validator = ValidationEngine(max_retries=2)
    validation_report = validator.validate_and_repair(bundle)
    execution_report = execute_schema(bundle, DB_PATH)

    assumptions = []
    clarifying_questions = []
    if "default_roles_assumed" in intent.constraints:
        assumptions.append("Assumed default roles: admin, member.")
    if "default_entity_assumed" in intent.constraints:
        assumptions.append("Assumed a default entity because none was specified.")

    if not intent.features:
        clarifying_questions.append("What core features should the app include?")
    if not intent.entities:
        clarifying_questions.append("What main entities should be managed?")

    return CompileResult(
        prompt=prompt,
        intent=intent,
        design=design,
        config=bundle,
        validation=validation_report,
        execution=execution_report,
        assumptions=assumptions,
        clarifying_questions=clarifying_questions,
    )


@app.post("/generate")
async def generate(request: GenerateRequest) -> Dict[str, Any]:
    result = compile_prompt(request.prompt)
    return result.model_dump()


@app.post("/validate")
async def validate(request: ValidateRequest) -> Dict[str, Any]:
    report = validate_bundle(request.config)
    return {
        "valid": len(report) == 0,
        "issues": [issue.model_dump() for issue in report],
    }


@app.post("/evaluate")
async def evaluate() -> Dict[str, Any]:
    return {
        "real": evaluate_prompts(REAL_PROMPTS),
        "edge": evaluate_prompts(EDGE_PROMPTS),
    }


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}
