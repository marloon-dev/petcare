#!/usr/bin/env python3
"""Gera o DER final (versão 2, normalizado até a 3FN) do minimundo PetCare em SVG."""

W_BOX = 300
HDR = 34
ROW = 23
TAG_W = 38
NAME_W = 160

C_HDR = "#1f3a5f"
C_NEW = "#2e6b4f"   # cabeçalho de tabelas criadas na normalização
C_PK = "#fff4cc"
C_FK = "#e6f0fa"
C_TXT = "#1b1b1b"
C_LINE = "#3a3a3a"

X0, X1, X2, X3 = 40, 420, 800, 1180

entities = {
    "TELEFONE_TUTOR": (X0, 100, True, [
        ("PK", "id_telefone", "INT"),
        ("", "numero", "VARCHAR(15)"),
        ("", "tipo", "VARCHAR(15)"),
        ("FK", "id_tutor", "INT"),
    ]),
    "TUTOR": (X0, 300, False, [
        ("PK", "id_tutor", "INT"),
        ("", "nome", "VARCHAR(100)"),
        ("UK", "cpf", "CHAR(11)"),
        ("", "email", "VARCHAR(100)"),
        ("", "logradouro", "VARCHAR(120)"),
        ("", "numero", "VARCHAR(10)"),
        ("", "complemento", "VARCHAR(60)"),
        ("", "bairro", "VARCHAR(60)"),
        ("", "cidade", "VARCHAR(60)"),
        ("", "uf", "CHAR(2)"),
        ("", "cep", "CHAR(8)"),
    ]),
    "ANIMAL": (X1, 420, False, [
        ("PK", "id_animal", "INT"),
        ("", "nome", "VARCHAR(60)"),
        ("", "sexo", "CHAR(1)"),
        ("", "data_nascimento", "DATE"),
        ("FK", "id_tutor", "INT"),
        ("FK", "id_raca", "INT"),
    ]),
    "RACA": (X1, 680, True, [
        ("PK", "id_raca", "INT"),
        ("", "nome", "VARCHAR(50)"),
        ("FK", "id_especie", "INT"),
    ]),
    "ESPECIE": (X1, 880, True, [
        ("PK", "id_especie", "INT"),
        ("UK", "nome", "VARCHAR(30)"),
    ]),
    "ATENDIMENTO": (X2, 100, False, [
        ("PK", "id_atendimento", "INT"),
        ("", "data_hora_inicio", "DATETIME"),
        ("", "queixa", "TEXT"),
        ("", "peso_aferido", "DECIMAL(5,2)"),
        ("", "diagnostico", "TEXT"),
        ("", "tratamento", "TEXT"),
        ("", "observacoes", "TEXT"),
        ("FK", "id_agendamento", "INT (único)"),
    ]),
    "AGENDAMENTO": (X2, 400, False, [
        ("PK", "id_agendamento", "INT"),
        ("", "data_hora", "DATETIME"),
        ("", "tipo_atendimento", "VARCHAR(30)"),
        ("", "status", "VARCHAR(15)"),
        ("", "observacoes", "TEXT"),
        ("FK", "id_animal", "INT"),
        ("FK", "id_veterinario", "INT"),
    ]),
    "APLICACAO_VACINA": (X2, 680, False, [
        ("PK", "id_aplicacao", "INT"),
        ("", "data_aplicacao", "DATE"),
        ("", "lote", "VARCHAR(30)"),
        ("FK", "id_animal", "INT"),
        ("FK", "id_vacina", "INT"),
        ("FK", "id_veterinario", "INT"),
    ]),
    "VACINA": (X2, 940, False, [
        ("PK", "id_vacina", "INT"),
        ("", "nome", "VARCHAR(80)"),
        ("", "fabricante", "VARCHAR(80)"),
        ("", "intervalo_reforco_dias", "INT"),
        ("FK", "id_especie", "INT"),
    ]),
    "PRESCRICAO": (X3, 110, False, [
        ("PK", "id_prescricao", "INT"),
        ("", "medicamento", "VARCHAR(100)"),
        ("", "dosagem", "VARCHAR(50)"),
        ("", "frequencia", "VARCHAR(50)"),
        ("", "duracao_dias", "INT"),
        ("", "orientacoes", "TEXT"),
        ("FK", "id_atendimento", "INT"),
    ]),
    "VETERINARIO": (X3, 520, False, [
        ("PK", "id_veterinario", "INT"),
        ("", "nome", "VARCHAR(100)"),
        ("UK", "crmv", "VARCHAR(15)"),
        ("", "telefone", "VARCHAR(15)"),
        ("", "email", "VARCHAR(100)"),
        ("FK", "id_especialidade", "INT"),
    ]),
    "ESPECIALIDADE": (X3, 800, True, [
        ("PK", "id_especialidade", "INT"),
        ("UK", "nome", "VARCHAR(60)"),
    ]),
}

CARD = {"one": "(1,1)", "many1": "(1,N)", "many0": "(0,N)", "opt": "(0,1)"}

# (pontos, marcador_inicio, marcador_fim, verbo)
edges = [
    ([(190, 300), (190, 226)], "one", "many1", "tem"),
    ([(340, 480), (420, 480)], "one", "many1", "possui"),
    ([(720, 470), (800, 470)], "one", "many0", "agenda"),
    ([(720, 560), (760, 560), (760, 740), (800, 740)], "one", "many0", "recebe"),
    ([(570, 680), (570, 592)], "one", "many0", "classifica"),
    ([(570, 880), (570, 783)], "one", "many1", "agrupa"),
    ([(720, 930), (760, 930), (760, 1000), (800, 1000)], "one", "many0", "indica", "C"),
    ([(950, 400), (950, 318)], "one", "opt", "gera"),
    ([(1100, 200), (1180, 200)], "one", "many0", "contém"),
    ([(950, 940), (950, 852)], "one", "many0", "é aplicada em"),
    ([(1180, 560), (1100, 560)], "one", "many0", "realiza"),
    ([(1180, 650), (1140, 650), (1140, 740), (1100, 740)], "one", "many0", "aplica", "C"),
    ([(1330, 800), (1330, 692)], "one", "many0", "define"),
]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def box(name, x, y, new, rows):
    h = HDR + ROW * len(rows)
    hdr = C_NEW if new else C_HDR
    out = ['<g>',
           f'<rect x="{x}" y="{y}" width="{W_BOX}" height="{h}" rx="6" fill="#ffffff" stroke="{hdr}" stroke-width="1.6"/>',
           f'<path d="M{x} {y+HDR} V{y+6} a6 6 0 0 1 6 -6 H{x+W_BOX-6} a6 6 0 0 1 6 6 V{y+HDR} Z" fill="{hdr}"/>',
           f'<text x="{x+W_BOX/2}" y="{y+22}" text-anchor="middle" font-size="15" font-weight="700" fill="#ffffff">{esc(name)}</text>']
    for i, (tag, attr, typ) in enumerate(rows):
        ry = y + HDR + i * ROW
        fill = C_PK if tag == "PK" else (C_FK if tag == "FK" else None)
        if fill:
            out.append(f'<rect x="{x+1}" y="{ry}" width="{W_BOX-2}" height="{ROW}" fill="{fill}"/>')
        if i > 0:
            out.append(f'<line x1="{x}" y1="{ry}" x2="{x+W_BOX}" y2="{ry}" stroke="#d9dee5" stroke-width="1"/>')
        ty = ry + 16
        weight = "700" if tag == "PK" else "400"
        deco = ' text-decoration="underline"' if tag == "PK" else ""
        if tag:
            out.append(f'<text x="{x+10}" y="{ty}" font-size="11" font-weight="700" fill="#5a6b80">{tag}</text>')
        out.append(f'<text x="{x+TAG_W}" y="{ty}" font-size="13" font-weight="{weight}" fill="{C_TXT}"{deco}>{esc(attr)}</text>')
        out.append(f'<text x="{x+TAG_W+NAME_W}" y="{ty}" font-size="12" fill="#55606e">{esc(typ)}</text>')
    out.append(f'<line x1="{x+TAG_W-6}" y1="{y+HDR}" x2="{x+TAG_W-6}" y2="{y+h}" stroke="#d9dee5" stroke-width="1"/>')
    out.append('</g>')
    return "\n".join(out)


def marker_defs():
    s = 'stroke="%s" stroke-width="1.6" fill="none"' % C_LINE
    crow = 'M-14 0 L0 -8 M-14 0 L0 0 M-14 0 L0 8'
    return f'''
<defs>
  <marker id="one" viewBox="-26 -10 28 20" refX="0" refY="0" markerWidth="28" markerHeight="20" markerUnits="userSpaceOnUse" orient="auto-start-reverse">
    <path d="M-8 -8 V8 M-14 -8 V8" {s}/>
  </marker>
  <marker id="many1" viewBox="-26 -10 28 20" refX="0" refY="0" markerWidth="28" markerHeight="20" markerUnits="userSpaceOnUse" orient="auto-start-reverse">
    <path d="{crow} M-19 -8 V8" {s}/>
  </marker>
  <marker id="many0" viewBox="-30 -10 32 20" refX="0" refY="0" markerWidth="32" markerHeight="20" markerUnits="userSpaceOnUse" orient="auto-start-reverse">
    <path d="{crow}" {s}/>
    <circle cx="-21" cy="0" r="5" fill="#ffffff" stroke="{C_LINE}" stroke-width="1.6"/>
  </marker>
  <marker id="opt" viewBox="-30 -10 32 20" refX="0" refY="0" markerWidth="32" markerHeight="20" markerUnits="userSpaceOnUse" orient="auto-start-reverse">
    <path d="M-8 -8 V8" {s}/>
    <circle cx="-18" cy="0" r="5" fill="#ffffff" stroke="{C_LINE}" stroke-width="1.6"/>
  </marker>
</defs>'''


def card_label(p, q, text):
    """Rótulo de cardinalidade junto ao ponto p, no segmento p→q."""
    (x, y), (qx, qy) = p, q
    if y == qy:  # horizontal: acima da linha
        d = 1 if qx > x else -1
        tx = x + d * 6 if d > 0 else x - 36
        return f'<text x="{tx}" y="{y-8}" font-size="12" font-weight="700" fill="#b0261c">{text}</text>'
    d = 1 if qy > y else -1  # vertical: à esquerda da linha
    ty = y + d * 18 + (4 if d > 0 else 4)
    return f'<text x="{x-42}" y="{ty}" font-size="12" font-weight="700" fill="#b0261c">{text}</text>'


def edge(pts, m0, m1, verb, side="R"):
    d = "M" + " L".join(f"{x} {y}" for x, y in pts)
    out = [f'<path d="{d}" fill="none" stroke="{C_LINE}" stroke-width="1.6" marker-start="url(#{m0})" marker-end="url(#{m1})"/>']
    out.append(card_label(pts[0], pts[1], CARD[m0]))
    out.append(card_label(pts[-1], pts[-2], CARD[m1]))
    # verbo no meio do segmento mais longo
    segs = list(zip(pts, pts[1:]))
    (ax, ay), (bx, by) = max(segs, key=lambda s: abs(s[0][0]-s[1][0]) + abs(s[0][1]-s[1][1]))
    mx, my = (ax + bx) / 2, (ay + by) / 2
    vw = len(verb) * 7.0 + 12
    if ay == by:
        rx, ry = mx - vw / 2, my + 7
    else:
        rx, ry = {"R": mx + 9, "L": mx - 9 - vw, "C": mx - vw / 2}[side], my - 9
    out.append(f'<rect x="{rx}" y="{ry}" width="{vw}" height="18" rx="9" fill="#fdf1e3" stroke="#d9822b" stroke-width="1"/>')
    out.append(f'<text x="{rx+6}" y="{ry+13}" font-size="12" font-style="italic" fill="#8a4b0f">{esc(verb)}</text>')
    return "\n".join(out)


def legend(x, y):
    out = [f'<rect x="{x}" y="{y}" width="300" height="340" rx="6" fill="#f7f9fb" stroke="#c4ccd6"/>',
           f'<text x="{x+14}" y="{y+26}" font-size="14" font-weight="700" fill="{C_TXT}">Legenda</text>']
    items = [("one", "exatamente um (1,1)"), ("opt", "zero ou um (0,1)"),
             ("many1", "um ou muitos (1,N)"), ("many0", "zero ou muitos (0,N)")]
    for i, (m, label) in enumerate(items):
        yy = y + 54 + i * 30
        out.append(f'<path d="M{x+20} {yy} L{x+80} {yy}" stroke="{C_LINE}" stroke-width="1.6" marker-end="url(#{m})"/>')
        out.append(f'<text x="{x+96}" y="{yy+4}" font-size="12" fill="{C_TXT}">{label}</text>')
    yy = y + 54 + 4 * 30
    out.append(f'<rect x="{x+20}" y="{yy-10}" width="26" height="16" fill="{C_PK}" stroke="#c4ccd6"/>')
    out.append(f'<text x="{x+56}" y="{yy+3}" font-size="12" fill="{C_TXT}">PK – chave primária</text>')
    out.append(f'<rect x="{x+20}" y="{yy+16}" width="26" height="16" fill="{C_FK}" stroke="#c4ccd6"/>')
    out.append(f'<text x="{x+56}" y="{yy+29}" font-size="12" fill="{C_TXT}">FK – chave estrangeira</text>')
    out.append(f'<text x="{x+20}" y="{yy+55}" font-size="12" fill="{C_TXT}"><tspan font-weight="700">UK</tspan> – valor único (chave candidata)</text>')
    out.append(f'<rect x="{x+20}" y="{yy+68}" width="26" height="16" rx="3" fill="{C_NEW}"/>')
    out.append(f'<text x="{x+56}" y="{yy+81}" font-size="12" fill="{C_TXT}">tabela criada na normalização</text>')
    out.append(f'<rect x="{x+20}" y="{yy+92}" width="26" height="16" rx="3" fill="{C_HDR}"/>')
    out.append(f'<text x="{x+56}" y="{yy+105}" font-size="12" fill="{C_TXT}">tabela do modelo inicial (revisada)</text>')
    out.append(f'<text x="{x+20}" y="{yy+132}" font-size="11.5" fill="#55606e">Versão 2: normalizada até a 3FN.</text>')
    return "\n".join(out)


WIDTH = HEIGHT = 1520
CONTENT_H = 1120
OFFSET = (HEIGHT - CONTENT_H) // 2  # centraliza para o recorte central do sips

parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" font-family="Helvetica, Arial, sans-serif">',
         f'<rect width="{WIDTH}" height="{HEIGHT}" fill="#ffffff"/>',
         f'<g transform="translate(0,{OFFSET})">',
         marker_defs(),
         f'<text x="40" y="44" font-size="22" font-weight="700" fill="{C_HDR}">PetCare – Diagrama Entidade-Relacionamento (versão final, 3FN)</text>',
         f'<text x="40" y="64" font-size="13" fill="#55606e">Sistema de Gestão para Clínica Veterinária · modelo lógico normalizado</text>']
for e in edges:
    parts.append(edge(*e))
for name, (x, y, new, rows) in entities.items():
    parts.append(box(name, x, y, new, rows))
parts.append(legend(X0, 700))
parts += ['</g>', '</svg>']

with open("DER_PetCare_v2_final.svg", "w", encoding="utf-8") as f:
    f.write("\n".join(parts))
print("ok", OFFSET)
