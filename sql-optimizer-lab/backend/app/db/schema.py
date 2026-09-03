from sqlalchemy import inspect
from app.db.connector import create_db_engine
from app.models.schemas import ConnectionConfig

def inspect_schema(cfg: ConnectionConfig):
    engine = create_db_engine(cfg)
    try:
        insp = inspect(engine)
        tables = []
        for table in insp.get_table_names()[:200]:
            cols = [{"name": c["name"], "type": str(c["type"]), "nullable": c.get("nullable", True)} for c in insp.get_columns(table)]
            idx = [{"name": x.get("name"), "columns": x.get("column_names", [])} for x in insp.get_indexes(table)]
            tables.append({"table": table, "columns": cols, "indexes": idx})
        return {"tables": tables}
    finally:
        engine.dispose()
