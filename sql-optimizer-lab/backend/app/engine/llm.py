from __future__ import annotations
import json
import os
from app.engine.rewrites import Rewrite

async def generate_llm_candidates(sql: str, dialect: str):
    if os.getenv("LLM_PROVIDER", "none") != "openai" or not os.getenv("OPENAI_API_KEY"):
        return []
    try:
        from openai import AsyncOpenAI
    except ImportError:
        return []
    client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])
    prompt = f"""Optimize this {dialect} SELECT query. Return JSON array with up to 4 objects having operator, sql, rationale. Preserve result semantics. Do not suggest DDL. Query:\n{sql}"""
    response = await client.responses.create(model=os.getenv("OPENAI_MODEL", "gpt-5-mini"), input=prompt)
    raw = response.output_text
    items = json.loads(raw)
    return [Rewrite(x["operator"], x["sql"], x["rationale"]) for x in items]
