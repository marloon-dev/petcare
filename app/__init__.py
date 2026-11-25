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

    @app.template_filter("kg")
    def _kg(value):
        return f"{float(value):.2f}".replace(".", ",") + " kg" if value is not None else "—"

    @app.template_filter("hora")
    def _hora(value):
        d = to_datetime(value)
        return d.strftime("%H:%M") if d else "—"

    dias_semana = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira",
                   "sexta-feira", "sábado", "domingo"]
    meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
             "agosto", "setembro", "outubro", "novembro", "dezembro"]

    @app.template_filter("data_extenso")
    def _data_extenso(value):
        d = to_date(value)
        if not d:
            return "—"
        texto = f"{dias_semana[d.weekday()]}, {d.day} de {meses[d.month - 1]} de {d.year}"
        return texto[0].upper() + texto[1:]

    @app.template_filter("idade")
    def _idade(value):
        from .views import hoje

        nascimento = to_date(value)
        if not nascimento:
            return "Idade desconhecida"
        ref = hoje()
        meses_total = (ref.year - nascimento.year) * 12 + ref.month - nascimento.month
        if ref.day < nascimento.day:
            meses_total -= 1
        anos, resto = divmod(max(meses_total, 0), 12)
        if anos:
            return f"{anos} ano{'s' if anos > 1 else ''}"
        return f"{resto} {'mês' if resto == 1 else 'meses'}"

    @app.context_processor
    def _contexto():
        from .views import hoje

        return {"data_hoje": hoje()}

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
