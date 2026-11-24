"""Cria um banco SQLite de demonstração a partir dos scripts MySQL.

Útil para testar a aplicação sem instalar o MySQL e para os testes
automatizados. Os scripts oficiais continuam sendo os de database/.
Aqui fazemos só as adaptações mínimas de sintaxe MySQL -> SQLite.
"""
import re
import sqlite3
from pathlib import Path

PASTA_SQL = Path(__file__).resolve().parent.parent / "database"


def mysql_para_sqlite(sql: str) -> str:
    sql = re.sub(r"^\s*(DROP DATABASE|CREATE DATABASE|USE)\b[^;]*;", "", sql, flags=re.M | re.S)
    sql = sql.replace("INT AUTO_INCREMENT PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT")
    sql = re.sub(r"\)\s*ENGINE\s*=\s*InnoDB", ")", sql)
    return sql.replace("START TRANSACTION;", "BEGIN;")


def criar_banco_demo(caminho: str, com_dados: bool = True) -> None:
    """Cria (ou recria) o arquivo SQLite com a estrutura e, opcionalmente, a carga de teste."""
    destino = Path(caminho)
    if destino.exists():
        destino.unlink()
    conn = sqlite3.connect(destino)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        scripts = ["01_ddl_criacao.sql"] + (["02_insert_povoamento.sql"] if com_dados else [])
        for nome in scripts:
            conn.executescript(mysql_para_sqlite((PASTA_SQL / nome).read_text(encoding="utf-8")))
        conn.commit()
    finally:
        conn.close()
