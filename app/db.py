"""Acesso ao banco de dados.

Usa SQLAlchemy Core com SQL escrito à mão (text), para que as consultas
fiquem iguais às estudadas na disciplina. As consultas evitam funções
específicas de um SGBD (como CURDATE ou DATE_ADD): cálculos de data são
feitos em Python. Assim o mesmo código roda no MySQL (produção) e no
SQLite (testes automatizados).
"""
from datetime import date, datetime

from flask import current_app, g
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine

_engines = {}


def get_engine() -> Engine:
    url = current_app.config["DATABASE_URL"]
    if url not in _engines:
        engine = create_engine(url, pool_pre_ping=True, future=True)
        if url.startswith("sqlite"):
            # O SQLite só aplica chaves estrangeiras com este PRAGMA.
            @event.listens_for(engine, "connect")
            def _fk_on(dbapi_conn, _record):
                dbapi_conn.execute("PRAGMA foreign_keys = ON")

        _engines[url] = engine
    return _engines[url]


def query(sql, **params):
    """Executa um SELECT e devolve uma lista de dicionários."""
    with get_engine().connect() as conn:
        return [dict(row) for row in conn.execute(text(sql), params).mappings()]


def query_one(sql, **params):
    rows = query(sql, **params)
    return rows[0] if rows else None


def transaction():
    """Abre uma transação: confirma no final ou desfaz tudo se houver erro."""
    return get_engine().begin()


def run(conn, sql, **params):
    """Executa INSERT/UPDATE/DELETE dentro de uma transação aberta."""
    return conn.execute(text(sql), params)


def to_date(value):
    """Converte o valor vindo do banco (date, datetime ou texto) em date."""
    if value is None or isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    return date.fromisoformat(str(value)[:10])


def to_datetime(value):
    if value is None or isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value))
