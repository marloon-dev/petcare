"""Testes das telas e regras de negócio do PetCare (banco SQLite com a carga de teste)."""
import pytest


def texto(resposta):
    return resposta.get_data(as_text=True)


# ---------------------------------------------------------------------------
# Telas carregam
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("url", [
    "/", "/tutores", "/tutores?q=maria", "/tutores/1", "/tutores/novo",
    "/animais", "/animais/4", "/animais/10", "/animais/novo",
    "/agenda", "/agenda?status=Todos", "/agenda?status=Cancelado", "/agenda/novo",
    "/agenda/12/atender", "/vacinas", "/busca", "/busca?q=thor",
])
def test_telas_respondem(client, url):
    assert client.get(url).status_code == 200


def test_registro_inexistente_retorna_404(client):
    assert client.get("/animais/999").status_code == 404
    assert client.get("/tutores/999").status_code == 404


def test_painel_mostra_totais_e_alertas(client):
    html = texto(client.get("/"))
    assert "Pipoca" in html and "Mixomatose" in html      # vacina vencida
    assert "Luna" in html                                 # V10 vencida
    assert "Remarcação da consulta cancelada" not in html  # o painel não mostra observações
    assert 'data-total="agendados">4</strong>' in html


def test_prontuario_mostra_historico_e_peso_atual(client):
    html = texto(client.get("/animais/4"))  # Thor
    assert "Golden Retriever" in html and "Cão" in html   # espécie obtida pela raça
    assert "Dermatite alérgica" in html
    assert "Prednisolona" in html
    assert "32,60 kg" in html                             # peso do atendimento mais recente


# ---------------------------------------------------------------------------
# Tutores e animais
# ---------------------------------------------------------------------------
NOVO_TUTOR = {
    "nome": "Paula Teste", "cpf": "123.456.789-09", "email": "", "celular": "(11) 91234-5678",
    "telefone2": "1122223333", "tipo2": "Residencial", "logradouro": "Rua Teste",
    "numero": "10", "complemento": "", "bairro": "Centro", "cidade": "São Paulo", "uf": "SP",
    "cep": "01000-000",
}


def test_cadastrar_tutor_com_dois_telefones(client, consulta):
    resposta = client.post("/tutores/novo", data=NOVO_TUTOR)
    assert resposta.status_code == 302 and "/animais/novo?tutor=" in resposta.headers["Location"]
    tutor = consulta("SELECT * FROM tutor WHERE cpf = '12345678909'")[0]
    telefones = consulta("SELECT tipo FROM telefone_tutor WHERE id_tutor = :id ORDER BY tipo",
                         id=tutor["id_tutor"])
    assert [t["tipo"] for t in telefones] == ["Celular", "Residencial"]
    assert tutor["email"] is None and tutor["cep"] == "01000000"


def test_cpf_duplicado_e_recusado(client, consulta):
    dados = {**NOVO_TUTOR, "cpf": "10120230340"}  # CPF da Maria Oliveira
    html = texto(client.post("/tutores/novo", data=dados))
    assert "Já existe um tutor com este CPF" in html
    assert consulta("SELECT COUNT(*) AS n FROM tutor")[0]["n"] == 6


def test_validacao_do_tutor(client):
    html = texto(client.post("/tutores/novo", data={**NOVO_TUTOR, "cpf": "123", "uf": "XX"}))
    assert "O CPF deve ter 11 dígitos" in html and "UF inválida" in html


def test_cadastrar_animal_sem_data_de_nascimento(client, consulta):
    resposta = client.post("/animais/novo", data={
        "nome": "Bidu", "sexo": "M", "data_nascimento": "", "id_tutor": "2", "id_raca": "1"})
    assert resposta.status_code == 302
    animal = consulta("SELECT * FROM animal WHERE nome = 'Bidu'")[0]
    assert animal["data_nascimento"] is None and animal["id_tutor"] == 2


def test_animal_com_nascimento_futuro_e_recusado(client):
    html = texto(client.post("/animais/novo", data={
        "nome": "Futuro", "sexo": "F", "data_nascimento": "2030-01-01", "id_tutor": "1", "id_raca": "1"}))
    assert "não pode ser futura" in html


# ---------------------------------------------------------------------------
# Agenda
# ---------------------------------------------------------------------------
def test_criar_agendamento(client, consulta):
    resposta = client.post("/agenda/novo", data={
        "id_animal": "3", "id_veterinario": "2", "tipo_atendimento": "Consulta",
        "data": "2026-12-10", "hora": "09:30", "observacoes": ""})
    assert resposta.status_code == 302
    ag = consulta("SELECT * FROM agendamento WHERE data_hora = '2026-12-10 09:30:00'")[0]
    assert ag["status"] == "Agendado" and ag["id_animal"] == 3


def test_conflito_de_horario_e_recusado(client):
    # A Dra. Ana Souza (id 1) já atende a Mia em 26/11 às 9h.
    html = texto(client.post("/agenda/novo", data={
        "id_animal": "3", "id_veterinario": "1", "tipo_atendimento": "Consulta",
        "data": "2026-11-26", "hora": "09:00"}))
    assert "já tem um agendamento neste horário" in html


def test_agendamento_no_passado_e_recusado(client):
    html = texto(client.post("/agenda/novo", data={
        "id_animal": "3", "id_veterinario": "1", "tipo_atendimento": "Consulta",
        "data": "2026-01-10", "hora": "09:00"}))
    assert "data passada" in html


def test_cancelar_agendamento_e_exclusao_logica(client, consulta):
    client.post("/agenda/14/cancelar")
    assert consulta("SELECT status FROM agendamento WHERE id_agendamento = 14")[0]["status"] == "Cancelado"
    # Cancelar de novo não altera nada.
    resposta = client.post("/agenda/14/cancelar", follow_redirects=True)
    assert "Só é possível cancelar agendamentos pendentes" in texto(resposta)


# ---------------------------------------------------------------------------
# Atendimento
# ---------------------------------------------------------------------------
def test_registrar_atendimento_com_prescricao(client, consulta):
    resposta = client.post("/agenda/12/atender", data={  # consulta da Mia
        "queixa": "Espirros frequentes", "peso_aferido": "3,85", "diagnostico": "Rinite viral",
        "tratamento": "Nebulização", "observacoes": "",
        "medicamento_1": "Lisina", "dosagem_1": "250 mg", "frequencia_1": "a cada 12 horas",
        "duracao_1": "15", "orientacoes_1": "Misturar na ração"})
    assert resposta.status_code == 302
    assert consulta("SELECT status FROM agendamento WHERE id_agendamento = 12")[0]["status"] == "Realizado"
    at = consulta("SELECT * FROM atendimento WHERE id_agendamento = 12")[0]
    assert float(at["peso_aferido"]) == 3.85
    prescricoes = consulta("SELECT * FROM prescricao WHERE id_atendimento = :id", id=at["id_atendimento"])
    assert len(prescricoes) == 1 and prescricoes[0]["duracao_dias"] == 15
    assert "3,85 kg" in texto(client.get("/animais/5"))  # peso atual atualizado


def test_atendimento_exige_campos_e_prescricao_completa(client, consulta):
    html = texto(client.post("/agenda/12/atender", data={
        "queixa": "", "diagnostico": "", "medicamento_1": "Lisina", "dosagem_1": "", "duracao_1": "0"}))
    assert "Queixa e diagnóstico são obrigatórios" in html
    assert "Prescrição 1" in html
    assert consulta("SELECT status FROM agendamento WHERE id_agendamento = 12")[0]["status"] == "Agendado"


def test_nao_atende_agendamento_ja_realizado(client):
    resposta = client.get("/agenda/1/atender", follow_redirects=True)
    assert "não está pendente" in texto(resposta)


# ---------------------------------------------------------------------------
# Vacinas
# ---------------------------------------------------------------------------
def test_vacina_de_outra_especie_e_recusada(client, consulta):
    # Nino é gato; a vacina 1 (V10) é para cães.
    html = texto(client.post("/vacinas", data={
        "id_animal": "2", "id_vacina": "1", "id_veterinario": "1",
        "data_aplicacao": "2026-11-24", "lote": "X1"}))
    assert "não é indicada para a espécie" in html
    assert consulta("SELECT COUNT(*) AS n FROM aplicacao_vacina")[0]["n"] == 11


def test_reforco_registrado_remove_alerta(client):
    linha_alerta = "<td data-rotulo=\"Vacina\">V4 (Quádrupla Felina)</td>"  # célula da tabela de alertas
    assert linha_alerta in texto(client.get("/vacinas"))  # Nino vence em 30/11
    resposta = client.post("/vacinas", data={
        "id_animal": "2", "id_vacina": "4", "id_veterinario": "1",
        "data_aplicacao": "2026-11-24", "lote": "ZT2611F"})
    assert resposta.status_code == 302
    assert linha_alerta not in texto(client.get("/vacinas"))  # reforço passou para 2027


def test_dose_duplicada_e_recusada(client):
    dados = {"id_animal": "7", "id_vacina": "4", "id_veterinario": "4",
             "data_aplicacao": "2026-11-12", "lote": "ZT2610F"}  # já registrada na carga
    assert "já foi registrada" in texto(client.post("/vacinas", data=dados))


# ---------------------------------------------------------------------------
# Busca geral e interface
# ---------------------------------------------------------------------------
def test_busca_geral_encontra_tutor_e_animal(client):
    html = texto(client.get("/busca?q=Maria"))
    assert "Maria Oliveira" in html            # tutor pelo nome
    assert "Luna" in html and "Nino" in html   # animais da tutora


def test_busca_geral_por_cpf_com_pontuacao(client, consulta):
    cpf = consulta("SELECT cpf FROM tutor WHERE id_tutor = 3")[0]["cpf"]
    formatado = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    assert "Fernanda Rocha" in texto(client.get("/busca", query_string={"q": formatado}))


def test_busca_sem_resultado(client):
    html = texto(client.get("/busca?q=zzzz"))
    assert "Nenhum tutor encontrado" in html and "Nenhum animal encontrado" in html


def test_idade_e_data_por_extenso(client):
    html = texto(client.get("/animais/10"))   # Max: sem data de nascimento
    assert "Idade desconhecida" in html
    assert "Terça-feira, 24 de novembro de 2026" in texto(client.get("/"))


def test_agenda_mostra_contagem_por_status(client):
    html = texto(client.get("/agenda"))
    assert 'aria-current="page"' in html and 'class="contagem">4<' in html
