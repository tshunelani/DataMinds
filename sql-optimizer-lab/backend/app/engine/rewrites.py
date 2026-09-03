from __future__ import annotations
from dataclasses import dataclass
import re
import sqlglot
from sqlglot import exp

@dataclass
class Rewrite:
    operator: str
    sql: str
    rationale: str
    executable: bool = True


def _render(tree, dialect: str):
    mapping = {"postgresql": "postgres", "mssql": "tsql", "mysql": "mysql", "sqlite": "sqlite"}
    return tree.sql(dialect=mapping.get(dialect, dialect))


def generate_rule_candidates(sql: str, dialect: str) -> list[Rewrite]:
    tree = sqlglot.parse_one(sql, read=mapping_read(dialect))
    out: list[Rewrite] = []

    if tree.find(exp.Distinct):
        t = tree.copy()
        distinct = t.find(exp.Distinct)
        if distinct:
            parent = distinct.parent
            if parent is not None:
                parent.set("distinct", None)
            out.append(Rewrite("remove_distinct", _render(t, dialect), "Removes DISTINCT when the query shape may not require duplicate elimination. Validate semantic equivalence."))

    # Make a safe-looking IN rewrite for OR equality chains.
    t = tree.copy()
    changed = False
    for node in list(t.find_all(exp.Or)):
        comparisons = []
        current = node
        while isinstance(current, exp.Or):
            comparisons.append(current.left)
            current = current.right
        comparisons.append(current)
        if comparisons and all(isinstance(c, exp.EQ) for c in comparisons):
            cols = [c.left.sql() for c in comparisons]
            if len(set(cols)) == 1:
                values = [c.right.copy() for c in comparisons]
                node.replace(exp.In(this=comparisons[0].left.copy(), expressions=values))
                changed = True
    if changed:
        out.append(Rewrite("or_to_in", _render(t, dialect), "Collapses repeated equality predicates into IN, reducing predicate complexity."))

    # Correlated EXISTS -> advisory candidate only. We do not synthesize arbitrary joins unless the structure is very simple.
    for exists in tree.find_all(exp.Exists):
        sub = exists.this
        if isinstance(sub, exp.Subquery) and sub.find(exp.EQ):
            out.append(Rewrite("exists_to_join_advisory", sql, "Detected EXISTS/correlation candidate. Prefer EXISTS for existence checks when only presence is needed; join conversion is schema-sensitive and remains advisory.", False))
            break

    for in_expr in tree.find_all(exp.In):
        if isinstance(in_expr.args.get("query"), exp.Subquery):
            out.append(Rewrite("in_to_exists_advisory", sql, "For correlated or large subqueries, compare IN with EXISTS; EXISTS can stop after the first match, but NULL semantics must be preserved.", False))
            break

    if tree.find(exp.Star):
        out.append(Rewrite("explicit_projection_advisory", sql, "SELECT * may read and return unnecessary columns. Replace it with the required columns after inspecting the schema.", False))

    for join in tree.find_all(exp.Join):
        kind = (join.args.get("kind") or "").upper()
        side = (join.args.get("side") or "").upper()
        if kind == "CROSS":
            out.append(Rewrite("cross_join_advisory", sql, "CROSS JOIN creates a Cartesian product. Compare it with an explicit INNER JOIN predicate and verify the intended cardinality.", False))
        elif join.args.get("method") == "LATERAL" or "LATERAL" in join.sql().upper():
            out.append(Rewrite("lateral_join_advisory", sql, "LATERAL joins can be useful for per-row lookups but may repeatedly execute a subquery; compare them with an indexed join.", False))
        elif side == "LEFT":
            out.append(Rewrite("left_join_advisory", sql, "Compare LEFT JOIN with INNER JOIN only when unmatched left rows are not required; INNER JOIN can reduce rows earlier.", False))

    if tree.args.get("having"):
        out.append(Rewrite("having_filter_advisory", sql, "Move non-aggregate HAVING predicates into WHERE when semantics allow, so rows are filtered before grouping.", False))

    for like in tree.find_all(exp.Like):
        pattern = like.expression
        if isinstance(pattern, exp.Literal) and pattern.is_string:
            value = pattern.this
            if value.startswith("%"):
                out.append(Rewrite("leading_like_wildcard_advisory", sql, "A leading LIKE wildcard prevents normal index seeks; use a searchable prefix, full-text index, or another search strategy.", False))
            elif value.endswith("%"):
                out.append(Rewrite("prefix_like_index_advisory", sql, "A trailing-only LIKE wildcard can use an index when collation and data type permit; verify the execution plan.", False))

    if re.search(r"(?:=|<>|!=|<=|>=|<|>)\s*'[-+]?\d+(?:\.\d+)?'", sql):
        out.append(Rewrite("implicit_conversion_advisory", sql, "A quoted numeric literal may force an implicit type conversion. Match comparison literals and parameters to the column data type.", False))

    # Dialect-aware SARGable rewrites for common ISO/timestamp date filters.
    if dialect == "sqlite":
        m = re.search(r"(?i)date\((\w+(?:\.\w+)?)\)\s*>=\s*date\('now',\s*'(-?\d+)\s+day'\)", sql)
        if m:
            tsql = re.sub(r"(?i)date\((\w+(?:\.\w+)?)\)\s*>=\s*date\('now',\s*'(-?\d+)\s+day'\)", r"\1 >= datetime('now', '\2 day')", sql, count=1)
            out.append(Rewrite("sargable_date_range", tsql, "Moves the date function off the column so an index on the timestamp column can be considered by the optimizer. Assumes ISO-8601 timestamp text or a compatible timestamp type."))
    if dialect == "postgresql":
        m = re.search(r"(?i)date\((\w+(?:\.\w+)?)\)\s*>=\s*date\('now',\s*'(-?\d+)\s+day'\)", sql)
        if m:
            days = m.group(2)
            tsql = re.sub(r"(?i)date\((\w+(?:\.\w+)?)\)\s*>=\s*date\('now',\s*'(-?\d+)\s+day'\)", rf"\1 >= CURRENT_DATE + INTERVAL '{days} days'", sql, count=1)
            out.append(Rewrite("sargable_date_range", tsql, "Moves the date function off the column so a timestamp/date index can be used. Validate timezone and boundary semantics."))

    # SARGability advisory from common DATE(column) pattern.
    if re.search(r"(?i)\b(date|lower|upper|cast)\s*\(\s*[A-Za-z_][\w.]*\s*\)", sql):
        out.append(Rewrite("sargability_advisory", sql, "Detected a function over a likely predicate column. Rewrite to a range predicate when the data type/index semantics allow it."))

    # UNION -> UNION ALL when duplicate elimination appears unnecessary is unsafe; expose as candidate explanation without altering semantics.
    if tree.find(exp.Union) and not tree.find(exp.Distinct):
        out.append(Rewrite("union_all_advisory", sql, "UNION may pay duplicate-elimination cost. Consider UNION ALL only if duplicate semantics are acceptable."))

    # Deduplicate identical SQL.
    seen = set()
    unique = []
    for item in out:
        normalized = sqlglot.parse_one(item.sql, read=mapping_read(dialect)).sql(dialect=mapping_write(dialect), pretty=True)
        key = normalized.strip().lower()
        if (item.executable and key == sql.strip().lower()) or (key in seen and item.executable):
            continue
        if key not in seen or not item.executable:
            seen.add(key)
            unique.append(Rewrite(item.operator, normalized, item.rationale, item.executable))
    return unique[:12]


def mapping_read(dialect: str) -> str:
    return {"postgresql": "postgres", "mssql": "tsql", "mysql": "mysql", "sqlite": "sqlite"}.get(dialect, dialect)

def mapping_write(dialect: str) -> str:
    return mapping_read(dialect)
