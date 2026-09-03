from sqlglot import parse_one, exp

ALLOWED_ROOTS = (exp.Select, exp.Union, exp.Subquery, exp.With, exp.Expression)

def validate_read_only(sql: str) -> None:
    statements = [s for s in sql.split(";") if s.strip()]
    if len(statements) != 1:
        raise ValueError("Only one SQL statement is allowed.")
    tree = parse_one(statements[0])
    forbidden = (exp.Insert, exp.Update, exp.Delete, exp.Create, exp.Drop, exp.Alter, exp.Merge, exp.Command)
    if tree.find(*forbidden):
        raise ValueError("Only read-only SELECT queries are allowed for optimization runs.")
    if not isinstance(tree, (exp.Select, exp.Union, exp.With)):
        # EXPLAIN and dialect-specific wrappers are handled by the executor, not by the user SQL.
        raise ValueError("The optimizer accepts SELECT/CTE/UNION queries only.")
