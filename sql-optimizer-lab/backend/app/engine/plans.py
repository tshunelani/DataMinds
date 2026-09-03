from __future__ import annotations
import json, re
from typing import Any


def _walk(obj: Any):
    if isinstance(obj, dict):
        yield obj
        for v in obj.values(): yield from _walk(v)
    elif isinstance(obj, list):
        for v in obj: yield from _walk(v)


def parse_postgres_plan(raw: str) -> dict:
    try:
        data = json.loads(raw)
        root = data[0]["Plan"] if isinstance(data, list) and data and "Plan" in data[0] else data["Plan"]
        nodes = list(_walk(root))
        scans = [n for n in nodes if n.get("Node Type", "").lower().endswith("scan")]
        seq = [n for n in scans if n.get("Node Type") == "Seq Scan"]
        sorts = [n for n in nodes if "Sort" in n.get("Node Type", "")]
        disk = sum(int(n.get("Temp Read Blocks", 0) or 0) for n in nodes)
        hits = sum(int(n.get("Shared Hit Blocks", 0) or 0) for n in nodes)
        reads = sum(int(n.get("Shared Read Blocks", 0) or 0) for n in nodes)
        rows = root.get("Actual Rows")
        return {
            "format": "postgres-json",
            "total_cost": root.get("Total Cost"),
            "actual_rows": rows,
            "seq_scans": len(seq),
            "sort_nodes": len(sorts),
            "cache_hits": hits,
            "disk_reads": reads,
            "temp_reads": disk,
            "nested_loops": sum(1 for n in nodes if n.get("Node Type") == "Nested Loop"),
            "warnings": ([f"{len(seq)} sequential scan node(s) detected"] if seq else []) + ([f"{len(sorts)} sort node(s) detected"] if sorts else []),
        }
    except Exception as exc:
        return {"format": "text", "warnings": [f"Plan parse failed: {exc}"]}


def parse_generic_explain(raw: str) -> dict:
    text = raw or ""
    return {
        "format": "text",
        "seq_scans": len(re.findall(r"(?i)seq scan|full table scan|table scan", text)),
        "sort_nodes": len(re.findall(r"(?i)sort", text)),
        "nested_loops": len(re.findall(r"(?i)nested loop", text)),
        "warnings": [],
    }
