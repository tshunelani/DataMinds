from __future__ import annotations
import json
from dataclasses import dataclass
from app.engine.rewrites import Rewrite
from app.core.config import get_settings

@dataclass
class LLMGeneration:
    candidates: list[Rewrite]
    status: str
    error: str | None = None


async def generate_llm_candidates(sql: str, dialect: str) -> LLMGeneration:
    settings = get_settings()
    if settings.llm_provider != "openai" or not settings.openai_api_key:
        return LLMGeneration([], "Unavailable: configure LLM_PROVIDER=openai and OPENAI_API_KEY")
    try:
        from openai import AsyncOpenAI
    except ImportError:
        return LLMGeneration([], "Unavailable: OpenAI package is not installed")
    try:
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        prompt = f"""Optimize this {dialect} SELECT query. Preserve result semantics and do not suggest DDL or DML.
For every candidate, provide a short operator name, executable SQL, and a concise human-readable rationale. Return no more than four candidates."""
        response = await client.responses.create(
            model=settings.openai_model,
            input=[{"role": "user", "content": f"{prompt}\n\nQuery:\n{sql}"}],
            text={"format": {"type": "json_schema", "name": "sql_candidates", "strict": True, "schema": {"type": "object", "properties": {"candidates": {"type": "array", "maxItems": 4, "items": {"type": "object", "properties": {"operator": {"type": "string"}, "sql": {"type": "string"}, "rationale": {"type": "string"}}, "required": ["operator", "sql", "rationale"], "additionalProperties": False}}}, "required": ["candidates"], "additionalProperties": False}}},
        )
        items = json.loads(response.output_text)["candidates"]
        candidates = [Rewrite(f"llm:{item['operator']}", item["sql"], item["rationale"]) for item in items]
        return LLMGeneration(candidates, f"OpenAI generated {len(candidates)} candidate(s)")
    except Exception as exc:
        return LLMGeneration([], "OpenAI generation failed", str(exc))
