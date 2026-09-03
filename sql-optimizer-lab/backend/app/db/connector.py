from __future__ import annotations
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from app.models.schemas import ConnectionConfig


def build_url(cfg: ConnectionConfig) -> str:
    if cfg.db_type == "sqlite":
        return f"sqlite:///{cfg.database}"
    user = quote_plus(cfg.user or "")
    password = quote_plus(cfg.password or "")
    host = cfg.host or "localhost"
    port = cfg.port
    ssl = ""
    if cfg.db_type == "postgresql":
        params = []
        if cfg.ssl_mode:
            params.append(f"sslmode={quote_plus(cfg.ssl_mode)}")
        suffix = ("?" + "&".join(params)) if params else ""
        return f"postgresql+psycopg://{user}:{password}@{host}:{port or 5432}/{cfg.database}{suffix}"
    if cfg.db_type == "mysql":
        return f"mysql+pymysql://{user}:{password}@{host}:{port or 3306}/{cfg.database}"
    if cfg.db_type == "mssql":
        odbc = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=" + host
        if port:
            odbc += f",{port}"
        odbc += ";DATABASE=" + cfg.database + ";UID=" + cfg.user + ";PWD=" + cfg.password + ";TrustServerCertificate=yes"
        if cfg.ssl_mode and cfg.ssl_mode.lower() in {"require", "verify-full", "strict"}:
            odbc = odbc.replace("TrustServerCertificate=yes", "Encrypt=yes;TrustServerCertificate=no")
        return "mssql+pyodbc:///?odbc_connect=" + quote_plus(odbc)
    raise ValueError("Unsupported database type")


def create_db_engine(cfg: ConnectionConfig) -> Engine:
    connect_args = {}
    if cfg.db_type == "sqlite":
        connect_args = {"check_same_thread": False}
    return create_engine(build_url(cfg), pool_pre_ping=True, future=True, connect_args=connect_args)


def ping(cfg: ConnectionConfig) -> dict:
    engine = create_db_engine(cfg)
    try:
        with engine.connect() as conn:
            value = conn.execute(text("SELECT 1")).scalar_one()
        return {"ok": True, "value": value}
    finally:
        engine.dispose()
