import pytest

from app import create_app
from app.demo import criar_banco_demo


@pytest.fixture
def app(tmp_path):
    banco = tmp_path / "teste.db"
    criar_banco_demo(str(banco))
    return create_app({
        "TESTING": True,
        "DATABASE_URL": f"sqlite:///{banco}",
        # Data fixa: a carga de teste foi montada para 24/11/2026.
        "HOJE": "2026-11-24",
    })


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def consulta(app):
    """Executa um SELECT direto no banco de teste (para conferir o resultado)."""
    from app.db import query

    def _consulta(sql, **params):
        with app.app_context():
            return query(sql, **params)

    return _consulta
