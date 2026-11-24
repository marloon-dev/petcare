"""PetCare - Sistema de Gestão para Clínica Veterinária (aplicação Flask)."""
import os

from dotenv import load_dotenv
from flask import Flask

from .db import to_date, to_datetime


def create_app(config=None):
    load_dotenv()
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-troque-esta-chave"),
        DATABASE_URL=os.getenv(
            "DATABASE_URL", "mysql+pymysql://root:@127.0.0.1:3306/petcare?charset=utf8mb4"
        ),
    )
    if config:
        app.config.update(config)

    @app.template_filter("data")
    def _data(value):
        d = to_date(value)
        return d.strftime("%d/%m/%Y") if d else "—"

    @app.template_filter("data_hora")
    def _data_hora(value):
        d = to_datetime(value)
        return d.strftime("%d/%m/%Y %H:%M") if d else "—"

    @app.template_filter("fone")
    def _fone(value):
        v = str(value or "")
        if len(v) == 11:
            return f"({v[:2]}) {v[2:7]}-{v[7:]}"
        if len(v) == 10:
            return f"({v[:2]}) {v[2:6]}-{v[6:]}"
        return v

    from . import views

    app.register_blueprint(views.bp)
    return app
