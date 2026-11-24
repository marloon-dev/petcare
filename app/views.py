"""Rotas (telas) da aplicação PetCare."""
import re
from datetime import date, datetime, timedelta

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from .db import query, query_one, run, to_date, to_datetime, transaction

bp = Blueprint("main", __name__)

TIPOS_ATENDIMENTO = ["Consulta", "Retorno", "Vacinação", "Procedimento", "Emergência"]
TIPOS_TELEFONE = ["Celular", "Residencial", "Comercial"]
UFS = ("AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO").split()
DIAS_ALERTA_VACINA = 30


# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------
def hoje() -> date:
    """Data atual. Nos testes, pode ser fixada pela configuração HOJE."""
    fixa = current_app.config.get("HOJE")
    return date.fromisoformat(fixa) if fixa else date.today()


def agora_str() -> str:
    return f"{hoje().isoformat()} {datetime.now().strftime('%H:%M:%S')}"


def so_digitos(valor: str) -> str:
    return re.sub(r"\D", "", valor or "")


def campo(nome: str) -> str:
    return (request.form.get(nome) or "").strip()


def opcional(valor: str):
    return valor or None


def alertas_vacina(id_animal=None, dias=DIAS_ALERTA_VACINA):
    """Doses vencidas ou que vencem nos próximos `dias` dias.

    A próxima dose não é armazenada (atributo derivado removido na 3FN):
    ela é calculada como data_aplicacao + intervalo_reforco_dias.
    Considera só a dose mais recente de cada vacina por animal.
    """
    sql = """
        SELECT an.id_animal, an.nome AS animal, tu.id_tutor, tu.nome AS tutor,
               va.nome AS vacina, va.intervalo_reforco_dias, av.data_aplicacao
        FROM aplicacao_vacina AS av
            INNER JOIN vacina AS va ON va.id_vacina = av.id_vacina
            INNER JOIN animal AS an ON an.id_animal = av.id_animal
            INNER JOIN tutor  AS tu ON tu.id_tutor  = an.id_tutor
        WHERE NOT EXISTS (
            SELECT 1 FROM aplicacao_vacina AS posterior
            WHERE posterior.id_animal = av.id_animal
              AND posterior.id_vacina = av.id_vacina
              AND posterior.data_aplicacao > av.data_aplicacao)
    """
    params = {}
    if id_animal is not None:
        sql += " AND av.id_animal = :id_animal"
        params["id_animal"] = id_animal
    limite = hoje() + timedelta(days=dias) if dias is not None else None
    resultado = []
    for row in query(sql, **params):
        proxima = to_date(row["data_aplicacao"]) + timedelta(days=row["intervalo_reforco_dias"])
        row["proxima_dose"] = proxima
        row["dias_restantes"] = (proxima - hoje()).days
        if limite is None or proxima <= limite:
            resultado.append(row)
    return sorted(resultado, key=lambda r: r["proxima_dose"])


def proximos_agendamentos(limite=10):
    return query(
        """
        SELECT ag.id_agendamento, ag.data_hora, ag.tipo_atendimento, ag.observacoes,
               an.id_animal, an.nome AS animal, tu.nome AS tutor, ve.nome AS veterinario
        FROM agendamento AS ag
            INNER JOIN animal      AS an ON an.id_animal      = ag.id_animal
            INNER JOIN tutor       AS tu ON tu.id_tutor       = an.id_tutor
            INNER JOIN veterinario AS ve ON ve.id_veterinario = ag.id_veterinario
        WHERE ag.status = 'Agendado' AND ag.data_hora >= :inicio
        ORDER BY ag.data_hora
        LIMIT :limite
        """,
        inicio=hoje().isoformat(),
        limite=limite,
    )


# ---------------------------------------------------------------------------
# Painel
# ---------------------------------------------------------------------------
@bp.route("/")
def painel():
    totais = query_one(
        """
        SELECT (SELECT COUNT(*) FROM tutor)  AS tutores,
               (SELECT COUNT(*) FROM animal) AS animais,
               (SELECT COUNT(*) FROM veterinario) AS veterinarios,
               (SELECT COUNT(*) FROM agendamento
                 WHERE status = 'Agendado' AND data_hora >= :inicio) AS agendados
        """,
        inicio=hoje().isoformat(),
    )
    return render_template(
        "painel.html",
        totais=totais,
        agenda=proximos_agendamentos(5),
        alertas=alertas_vacina(),
        hoje=hoje(),
    )


# ---------------------------------------------------------------------------
# Tutores
# ---------------------------------------------------------------------------
@bp.route("/tutores")
def tutores():
    busca = (request.args.get("q") or "").strip()
    rows = query(
        """
        SELECT tu.id_tutor, tu.nome, tu.cpf, tu.cidade, tu.uf,
               (SELECT COUNT(*) FROM animal AS an WHERE an.id_tutor = tu.id_tutor) AS animais,
               (SELECT MIN(te.numero) FROM telefone_tutor AS te
                 WHERE te.id_tutor = tu.id_tutor AND te.tipo = 'Celular') AS celular
        FROM tutor AS tu
        WHERE tu.nome LIKE :busca OR tu.cpf LIKE :busca
        ORDER BY tu.nome
        """,
        busca=f"%{busca}%",
    )
    return render_template("tutores.html", tutores=rows, busca=busca)


@bp.route("/tutores/<int:id_tutor>")
def tutor(id_tutor):
    dados = query_one("SELECT * FROM tutor WHERE id_tutor = :id", id=id_tutor) or abort(404)
    telefones = query(
        "SELECT numero, tipo FROM telefone_tutor WHERE id_tutor = :id ORDER BY tipo", id=id_tutor
    )
    animais = query(
        """
        SELECT an.id_animal, an.nome, an.sexo, an.data_nascimento,
               ra.nome AS raca, es.nome AS especie
        FROM animal AS an
            INNER JOIN raca    AS ra ON ra.id_raca    = an.id_raca
            INNER JOIN especie AS es ON es.id_especie = ra.id_especie
        WHERE an.id_tutor = :id
        ORDER BY an.nome
        """,
        id=id_tutor,
    )
    return render_template("tutor.html", tutor=dados, telefones=telefones, animais=animais)


@bp.route("/tutores/novo", methods=["GET", "POST"])
def tutor_novo():
    form = request.form if request.method == "POST" else {}
    if request.method == "POST":
        dados = {
            "nome": campo("nome"),
            "cpf": so_digitos(campo("cpf")),
            "email": opcional(campo("email")),
            "logradouro": campo("logradouro"),
            "numero": campo("numero"),
            "complemento": opcional(campo("complemento")),
            "bairro": campo("bairro"),
            "cidade": campo("cidade"),
            "uf": campo("uf").upper(),
            "cep": so_digitos(campo("cep")),
        }
        celular = so_digitos(campo("celular"))
        telefone2 = so_digitos(campo("telefone2"))
        tipo2 = campo("tipo2") or "Residencial"

        erros = []
        for obrigatorio in ("nome", "logradouro", "numero", "bairro", "cidade"):
            if not dados[obrigatorio]:
                erros.append(f"Preencha o campo {obrigatorio}.")
        if len(dados["cpf"]) != 11:
            erros.append("O CPF deve ter 11 dígitos.")
        if dados["uf"] not in UFS:
            erros.append("UF inválida.")
        if len(dados["cep"]) != 8:
            erros.append("O CEP deve ter 8 dígitos.")
        if len(celular) not in (10, 11):
            erros.append("Informe um celular com DDD (10 ou 11 dígitos).")
        if telefone2 and len(telefone2) not in (10, 11):
            erros.append("O segundo telefone deve ter DDD (10 ou 11 dígitos).")
        if tipo2 not in TIPOS_TELEFONE:
            erros.append("Tipo de telefone inválido.")

        if not erros:
            try:
                with transaction() as conn:
                    resultado = run(
                        conn,
                        """
                        INSERT INTO tutor (nome, cpf, email, logradouro, numero, complemento,
                                           bairro, cidade, uf, cep)
                        VALUES (:nome, :cpf, :email, :logradouro, :numero, :complemento,
                                :bairro, :cidade, :uf, :cep)
                        """,
                        **dados,
                    )
                    id_tutor = resultado.lastrowid
                    run(conn, "INSERT INTO telefone_tutor (numero, tipo, id_tutor) VALUES (:n, 'Celular', :t)",
                        n=celular, t=id_tutor)
                    if telefone2 and telefone2 != celular:
                        run(conn, "INSERT INTO telefone_tutor (numero, tipo, id_tutor) VALUES (:n, :tipo, :t)",
                            n=telefone2, tipo=tipo2, t=id_tutor)
                flash("Tutor cadastrado. Agora cadastre o animal.", "ok")
                return redirect(url_for("main.animal_novo", tutor=id_tutor))
            except IntegrityError:
                erros.append("Já existe um tutor com este CPF.")
        for erro in erros:
            flash(erro, "erro")
    return render_template("tutor_form.html", form=form, ufs=UFS, tipos_telefone=TIPOS_TELEFONE)


# ---------------------------------------------------------------------------
# Animais
# ---------------------------------------------------------------------------
@bp.route("/animais")
def animais():
    busca = (request.args.get("q") or "").strip()
    rows = query(
        """
        SELECT an.id_animal, an.nome, an.sexo, an.data_nascimento,
               ra.nome AS raca, es.nome AS especie, tu.id_tutor, tu.nome AS tutor
        FROM animal AS an
            INNER JOIN raca    AS ra ON ra.id_raca    = an.id_raca
            INNER JOIN especie AS es ON es.id_especie = ra.id_especie
            INNER JOIN tutor   AS tu ON tu.id_tutor   = an.id_tutor
        WHERE an.nome LIKE :busca OR tu.nome LIKE :busca
        ORDER BY an.nome
        """,
        busca=f"%{busca}%",
    )
    return render_template("animais.html", animais=rows, busca=busca)


@bp.route("/animais/<int:id_animal>")
def animal(id_animal):
    dados = query_one(
        """
        SELECT an.*, ra.nome AS raca, es.nome AS especie, tu.nome AS tutor
        FROM animal AS an
            INNER JOIN raca    AS ra ON ra.id_raca    = an.id_raca
            INNER JOIN especie AS es ON es.id_especie = ra.id_especie
            INNER JOIN tutor   AS tu ON tu.id_tutor   = an.id_tutor
        WHERE an.id_animal = :id
        """,
        id=id_animal,
    ) or abort(404)

    # Peso atual = peso do atendimento mais recente (não é armazenado em ANIMAL).
    peso = query_one(
        """
        SELECT at.peso_aferido, at.data_hora_inicio
        FROM atendimento AS at
            INNER JOIN agendamento AS ag ON ag.id_agendamento = at.id_agendamento
        WHERE ag.id_animal = :id AND at.peso_aferido IS NOT NULL
        ORDER BY at.data_hora_inicio DESC
        LIMIT 1
        """,
        id=id_animal,
    )
    atendimentos = query(
        """
        SELECT at.id_atendimento, at.data_hora_inicio, at.queixa, at.peso_aferido,
               at.diagnostico, at.tratamento, ag.tipo_atendimento, ve.nome AS veterinario
        FROM atendimento AS at
            INNER JOIN agendamento AS ag ON ag.id_agendamento = at.id_agendamento
            INNER JOIN veterinario AS ve ON ve.id_veterinario = ag.id_veterinario
        WHERE ag.id_animal = :id
        ORDER BY at.data_hora_inicio DESC
        """,
        id=id_animal,
    )
    prescricoes = query(
        """
        SELECT pr.* FROM prescricao AS pr
            INNER JOIN atendimento AS at ON at.id_atendimento = pr.id_atendimento
            INNER JOIN agendamento AS ag ON ag.id_agendamento = at.id_agendamento
        WHERE ag.id_animal = :id
        ORDER BY pr.id_prescricao
        """,
        id=id_animal,
    )
    for at in atendimentos:
        at["prescricoes"] = [p for p in prescricoes if p["id_atendimento"] == at["id_atendimento"]]

    vacinas = query(
        """
        SELECT av.data_aplicacao, av.lote, va.nome AS vacina, va.intervalo_reforco_dias,
               ve.nome AS veterinario
        FROM aplicacao_vacina AS av
            INNER JOIN vacina      AS va ON va.id_vacina      = av.id_vacina
            INNER JOIN veterinario AS ve ON ve.id_veterinario = av.id_veterinario
        WHERE av.id_animal = :id
        ORDER BY av.data_aplicacao DESC
        """,
        id=id_animal,
    )
    agendamentos = query(
        """
        SELECT ag.id_agendamento, ag.data_hora, ag.tipo_atendimento, ag.status, ve.nome AS veterinario
        FROM agendamento AS ag
            INNER JOIN veterinario AS ve ON ve.id_veterinario = ag.id_veterinario
        WHERE ag.id_animal = :id AND ag.status = 'Agendado'
        ORDER BY ag.data_hora
        """,
        id=id_animal,
    )
    return render_template(
        "animal.html",
        animal=dados,
        peso=peso,
        atendimentos=atendimentos,
        vacinas=vacinas,
        alertas=alertas_vacina(id_animal=id_animal, dias=None),
        agendamentos=agendamentos,
        hoje=hoje(),
    )


@bp.route("/animais/novo", methods=["GET", "POST"])
def animal_novo():
    form = request.form if request.method == "POST" else {"id_tutor": request.args.get("tutor", "")}
    if request.method == "POST":
        nome, sexo = campo("nome"), campo("sexo")
        nascimento = opcional(campo("data_nascimento"))
        id_tutor, id_raca = campo("id_tutor"), campo("id_raca")
        erros = []
        if not nome:
            erros.append("Informe o nome do animal.")
        if sexo not in ("M", "F"):
            erros.append("Selecione o sexo.")
        if not id_tutor or not id_raca:
            erros.append("Selecione o tutor e a raça.")
        if nascimento and nascimento > hoje().isoformat():
            erros.append("A data de nascimento não pode ser futura.")
        if not erros:
            try:
                with transaction() as conn:
                    resultado = run(
                        conn,
                        """
                        INSERT INTO animal (nome, sexo, data_nascimento, id_tutor, id_raca)
                        VALUES (:nome, :sexo, :nasc, :tutor, :raca)
                        """,
                        nome=nome, sexo=sexo, nasc=nascimento, tutor=int(id_tutor), raca=int(id_raca),
                    )
                flash("Animal cadastrado.", "ok")
                return redirect(url_for("main.animal", id_animal=resultado.lastrowid))
            except (IntegrityError, ValueError):
                erros.append("Tutor ou raça inválidos.")
        for erro in erros:
            flash(erro, "erro")
    return render_template(
        "animal_form.html",
        form=form,
        tutores=query("SELECT id_tutor, nome, cpf FROM tutor ORDER BY nome"),
        racas=query(
            """
            SELECT ra.id_raca, ra.nome, es.nome AS especie
            FROM raca AS ra INNER JOIN especie AS es ON es.id_especie = ra.id_especie
            ORDER BY es.nome, ra.nome
            """
        ),
    )


# ---------------------------------------------------------------------------
# Agenda
# ---------------------------------------------------------------------------
@bp.route("/agenda")
def agenda():
    filtro = request.args.get("status", "Agendado")
    sql = """
        SELECT ag.id_agendamento, ag.data_hora, ag.tipo_atendimento, ag.status, ag.observacoes,
               an.id_animal, an.nome AS animal, tu.nome AS tutor, ve.nome AS veterinario
        FROM agendamento AS ag
            INNER JOIN animal      AS an ON an.id_animal      = ag.id_animal
            INNER JOIN tutor       AS tu ON tu.id_tutor       = an.id_tutor
            INNER JOIN veterinario AS ve ON ve.id_veterinario = ag.id_veterinario
    """
    params = {}
    if filtro in ("Agendado", "Realizado", "Cancelado"):
        sql += " WHERE ag.status = :status"
        params["status"] = filtro
    sql += " ORDER BY ag.data_hora " + ("ASC" if filtro == "Agendado" else "DESC")
    return render_template("agenda.html", agendamentos=query(sql, **params), filtro=filtro)


def _opcoes_agendamento():
    return {
        "animais": query(
            """
            SELECT an.id_animal, an.nome, tu.nome AS tutor
            FROM animal AS an INNER JOIN tutor AS tu ON tu.id_tutor = an.id_tutor
            ORDER BY an.nome
            """
        ),
        "veterinarios": query(
            """
            SELECT ve.id_veterinario, ve.nome, es.nome AS especialidade
            FROM veterinario AS ve
                INNER JOIN especialidade AS es ON es.id_especialidade = ve.id_especialidade
            ORDER BY ve.nome
            """
        ),
        "tipos": TIPOS_ATENDIMENTO,
    }


@bp.route("/agenda/novo", methods=["GET", "POST"])
def agendamento_novo():
    form = request.form if request.method == "POST" else {"id_animal": request.args.get("animal", "")}
    if request.method == "POST":
        dia, hora, tipo = campo("data"), campo("hora"), campo("tipo_atendimento")
        id_animal, id_vet = campo("id_animal"), campo("id_veterinario")
        erros = []
        if not (dia and hora):
            erros.append("Informe a data e o horário.")
        elif dia < hoje().isoformat():
            erros.append("Não é possível agendar em uma data passada.")
        if tipo not in TIPOS_ATENDIMENTO:
            erros.append("Selecione o tipo de atendimento.")
        if not id_animal or not id_vet:
            erros.append("Selecione o animal e o veterinário.")
        if not erros:
            try:
                with transaction() as conn:
                    run(
                        conn,
                        """
                        INSERT INTO agendamento (data_hora, tipo_atendimento, status, observacoes,
                                                 id_animal, id_veterinario)
                        VALUES (:dh, :tipo, 'Agendado', :obs, :animal, :vet)
                        """,
                        dh=f"{dia} {hora[:5]}:00", tipo=tipo, obs=opcional(campo("observacoes")),
                        animal=int(id_animal), vet=int(id_vet),
                    )
                flash("Agendamento criado.", "ok")
                return redirect(url_for("main.agenda"))
            except IntegrityError:
                # UNIQUE (id_veterinario, data_hora) impede conflito de agenda.
                erros.append("Este veterinário já tem um agendamento neste horário.")
        for erro in erros:
            flash(erro, "erro")
    return render_template("agendamento_form.html", form=form, **_opcoes_agendamento())


@bp.route("/agenda/<int:id_agendamento>/cancelar", methods=["POST"])
def agendamento_cancelar(id_agendamento):
    # Exclusão lógica: o registro é mantido, apenas o status muda.
    with transaction() as conn:
        resultado = run(
            conn,
            "UPDATE agendamento SET status = 'Cancelado' WHERE id_agendamento = :id AND status = 'Agendado'",
            id=id_agendamento,
        )
    if resultado.rowcount:
        flash("Agendamento cancelado.", "ok")
    else:
        flash("Só é possível cancelar agendamentos pendentes.", "erro")
    return redirect(request.referrer or url_for("main.agenda"))


@bp.route("/agenda/<int:id_agendamento>/atender", methods=["GET", "POST"])
def atendimento_novo(id_agendamento):
    ag = query_one(
        """
        SELECT ag.*, an.nome AS animal, es.nome AS especie, tu.nome AS tutor, ve.nome AS veterinario
        FROM agendamento AS ag
            INNER JOIN animal      AS an ON an.id_animal      = ag.id_animal
            INNER JOIN raca        AS ra ON ra.id_raca        = an.id_raca
            INNER JOIN especie     AS es ON es.id_especie     = ra.id_especie
            INNER JOIN tutor       AS tu ON tu.id_tutor       = an.id_tutor
            INNER JOIN veterinario AS ve ON ve.id_veterinario = ag.id_veterinario
        WHERE ag.id_agendamento = :id
        """,
        id=id_agendamento,
    ) or abort(404)
    if ag["status"] != "Agendado":
        flash("Este agendamento não está pendente.", "erro")
        return redirect(url_for("main.animal", id_animal=ag["id_animal"]))

    form = request.form if request.method == "POST" else {}
    if request.method == "POST":
        queixa, diagnostico = campo("queixa"), campo("diagnostico")
        peso = campo("peso_aferido").replace(",", ".")
        erros = []
        if not queixa or not diagnostico:
            erros.append("Queixa e diagnóstico são obrigatórios.")
        try:
            peso_valor = float(peso) if peso else None
            if peso_valor is not None and peso_valor <= 0:
                raise ValueError
        except ValueError:
            peso_valor = None
            erros.append("Peso inválido.")

        prescricoes = []
        for i in range(1, 4):
            med = campo(f"medicamento_{i}")
            if not med:
                continue
            item = {
                "medicamento": med,
                "dosagem": campo(f"dosagem_{i}"),
                "frequencia": campo(f"frequencia_{i}"),
                "duracao": campo(f"duracao_{i}"),
                "orientacoes": opcional(campo(f"orientacoes_{i}")),
            }
            if not (item["dosagem"] and item["frequencia"] and item["duracao"].isdigit()
                    and int(item["duracao"]) > 0):
                erros.append(f"Prescrição {i}: informe dosagem, frequência e duração em dias.")
            prescricoes.append(item)

        if not erros:
            # Tudo em uma transação: atendimento, prescrições e status do agendamento.
            with transaction() as conn:
                resultado = run(
                    conn,
                    """
                    INSERT INTO atendimento (data_hora_inicio, queixa, peso_aferido, diagnostico,
                                             tratamento, observacoes, id_agendamento)
                    VALUES (:inicio, :queixa, :peso, :diag, :trat, :obs, :ag)
                    """,
                    inicio=agora_str(), queixa=queixa, peso=peso_valor, diag=diagnostico,
                    trat=opcional(campo("tratamento")), obs=opcional(campo("observacoes")),
                    ag=id_agendamento,
                )
                id_atendimento = resultado.lastrowid
                for p in prescricoes:
                    run(
                        conn,
                        """
                        INSERT INTO prescricao (medicamento, dosagem, frequencia, duracao_dias,
                                                orientacoes, id_atendimento)
                        VALUES (:medicamento, :dosagem, :frequencia, :duracao, :orientacoes, :at)
                        """,
                        at=id_atendimento, **{**p, "duracao": int(p["duracao"])},
                    )
                run(conn, "UPDATE agendamento SET status = 'Realizado' WHERE id_agendamento = :id",
                    id=id_agendamento)
            flash("Atendimento registrado.", "ok")
            return redirect(url_for("main.animal", id_animal=ag["id_animal"]))
        for erro in erros:
            flash(erro, "erro")
    return render_template("atendimento_form.html", ag=ag, form=form)


# ---------------------------------------------------------------------------
# Vacinas
# ---------------------------------------------------------------------------
@bp.route("/vacinas", methods=["GET", "POST"])
def vacinas():
    form = request.form if request.method == "POST" else {
        "id_animal": request.args.get("animal", ""),
        "data_aplicacao": hoje().isoformat(),
    }
    if request.method == "POST":
        id_animal, id_vacina, id_vet = campo("id_animal"), campo("id_vacina"), campo("id_veterinario")
        data_aplicacao, lote = campo("data_aplicacao"), campo("lote")
        erros = []
        if not (id_animal and id_vacina and id_vet and data_aplicacao and lote):
            erros.append("Preencha todos os campos.")
        elif data_aplicacao > hoje().isoformat():
            erros.append("A data de aplicação não pode ser futura.")
        else:
            # Regra de negócio: a vacina deve ser indicada para a espécie do animal.
            compativel = query_one(
                """
                SELECT 1 AS ok
                FROM animal AS an
                    INNER JOIN raca   AS ra ON ra.id_raca    = an.id_raca
                    INNER JOIN vacina AS va ON va.id_especie = ra.id_especie
                WHERE an.id_animal = :animal AND va.id_vacina = :vacina
                """,
                animal=id_animal, vacina=id_vacina,
            )
            if not compativel:
                erros.append("Esta vacina não é indicada para a espécie do animal.")
        if not erros:
            try:
                with transaction() as conn:
                    run(
                        conn,
                        """
                        INSERT INTO aplicacao_vacina (data_aplicacao, lote, id_animal, id_vacina, id_veterinario)
                        VALUES (:data, :lote, :animal, :vacina, :vet)
                        """,
                        data=data_aplicacao, lote=lote, animal=int(id_animal),
                        vacina=int(id_vacina), vet=int(id_vet),
                    )
                flash("Aplicação de vacina registrada.", "ok")
                return redirect(url_for("main.animal", id_animal=int(id_animal)))
            except IntegrityError:
                erros.append("Esta dose já foi registrada para o animal nesta data.")
        for erro in erros:
            flash(erro, "erro")

    return render_template(
        "vacinas.html",
        form=form,
        alertas=alertas_vacina(),
        animais=query(
            """
            SELECT an.id_animal, an.nome, es.nome AS especie, tu.nome AS tutor
            FROM animal AS an
                INNER JOIN raca    AS ra ON ra.id_raca    = an.id_raca
                INNER JOIN especie AS es ON es.id_especie = ra.id_especie
                INNER JOIN tutor   AS tu ON tu.id_tutor   = an.id_tutor
            ORDER BY an.nome
            """
        ),
        vacinas_lista=query(
            """
            SELECT va.id_vacina, va.nome, es.nome AS especie
            FROM vacina AS va INNER JOIN especie AS es ON es.id_especie = va.id_especie
            ORDER BY es.nome, va.nome
            """
        ),
        veterinarios=_opcoes_agendamento()["veterinarios"],
    )


@bp.app_errorhandler(404)
def nao_encontrado(_erro):
    return render_template("erro.html", mensagem="Registro não encontrado."), 404
