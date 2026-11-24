"""Ponto de entrada da aplicação PetCare.

Uso:
    flask --app run run --debug          # inicia o servidor em http://127.0.0.1:5000
    flask --app run criar-demo           # cria o banco SQLite de demonstração (demo.db)
"""
from pathlib import Path

import click

from app import create_app
from app.demo import criar_banco_demo

app = create_app()


@app.cli.command("criar-demo")
@click.option("--arquivo", default="demo.db", show_default=True, help="Arquivo SQLite a criar.")
def criar_demo(arquivo):
    """Cria um banco SQLite com a estrutura e a carga de teste do PetCare."""
    criar_banco_demo(arquivo)
    caminho = Path(arquivo).resolve()
    click.echo(f"Banco de demonstração criado em {caminho}")
    click.echo(f'Para usá-lo, defina no .env: DATABASE_URL=sqlite:///{caminho}')
