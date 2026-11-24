#!/usr/bin/env python3
"""Gera o DER inicial (versão 1) do minimundo PetCare em SVG."""

W_BOX = 320
HDR = 34
ROW = 23
TAG_W = 38
NAME_W = 168

C_HDR = "#1f3a5f"
C_BORDER = "#1f3a5f"
C_PK = "#fff4cc"
C_FK = "#e6f0fa"
C_TXT = "#1b1b1b"
C_LINE = "#3a3a3a"

entities = {
    "TUTOR": (60, 80, [
        ("PK", "id_tutor", "INT"),
        ("", "nome", "VARCHAR(100)"),
        ("UK", "cpf", "CHAR(11)"),
        ("", "email", "VARCHAR(100)"),
        ("", "telefones (multivalorado)", "VARCHAR(15) [N]"),
        ("", "endereco (composto)", ""),
        ("", "   └ logradouro", "VARCHAR(120)"),
        ("", "   └ numero", "VARCHAR(10)"),
        ("", "   └ bairro", "VARCHAR(60)"),
        ("", "   └ cidade", "VARCHAR(60)"),
        ("", "   └ uf", "CHAR(2)"),
        ("", "   └ cep", "CHAR(8)"),
    ]),
    "ANIMAL": (60, 480, [
        ("PK", "id_animal", "INT"),
        ("", "nome", "VARCHAR(60)"),
        ("", "especie", "VARCHAR(30)"),
        ("", "raca", "VARCHAR(50)"),
        ("", "sexo", "CHAR(1)"),
        ("", "data_nascimento", "DATE"),
        ("", "peso", "DECIMAL(5,2)"),
        ("FK", "id_tutor", "INT"),
    ]),
    "VACINA": (520, 80, [
        ("PK", "id_vacina", "INT"),
        ("", "nome", "VARCHAR(80)"),
        ("", "fabricante", "VARCHAR(80)"),
        ("", "especie_indicada", "VARCHAR(30)"),
        ("", "intervalo_reforco_dias", "INT"),
    ]),
    "APLICACAO_VACINA": (520, 300, [
        ("PK", "id_aplicacao", "INT"),
        ("", "data_aplicacao", "DATE"),
        ("", "lote", "VARCHAR(30)"),
        ("", "data_proxima_dose", "DATE"),
        ("FK", "id_animal", "INT"),
        ("FK", "id_vacina", "INT"),
        ("FK", "id_veterinario", "INT"),
    ]),
    "AGENDAMENTO": (520, 560, [
        ("PK", "id_agendamento", "INT"),
        ("", "data_hora", "DATETIME"),
        ("", "tipo_atendimento", "VARCHAR(30)"),
        ("", "status", "VARCHAR(15)"),
        ("", "observacoes", "TEXT"),
        ("FK", "id_animal", "INT"),
        ("FK", "id_veterinario", "INT"),
    ]),
    "ATENDIMENTO": (520, 830, [
        ("PK", "id_atendimento", "INT"),
        ("", "data_hora", "DATETIME"),
        ("", "queixa", "TEXT"),
        ("", "peso_aferido", "DECIMAL(5,2)"),
        ("", "diagnostico", "TEXT"),
        ("", "tratamento", "TEXT"),
        ("", "observacoes", "TEXT"),
        ("FK", "id_agendamento", "INT (opcional)"),
        ("FK", "id_animal", "INT"),
        ("FK", "id_veterinario", "INT"),
    ]),
    "VETERINARIO": (980, 560, [
        ("PK", "id_veterinario", "INT"),
        ("", "nome", "VARCHAR(100)"),
        ("UK", "crmv", "VARCHAR(15)"),
        ("", "especialidade", "VARCHAR(60)"),
        ("", "telefone", "VARCHAR(15)"),
        ("", "email", "VARCHAR(100)"),
    ]),
    "PRESCRICAO": (980, 900, [
        ("PK", "id_prescricao", "INT"),
        ("", "medicamento", "VARCHAR(100)"),
        ("", "dosagem", "VARCHAR(50)"),
        ("", "frequencia", "VARCHAR(50)"),
        ("", "duracao_dias", "INT"),
        ("", "orientacoes", "TEXT"),
        ("FK", "id_atendimento", "INT"),
    ]),
}

# (pontos, marcador_inicio, marcador_fim, verbo, pos_verbo, card_inicio, pos_ci, card_fim, pos_cf)
edges = [
    ([(220, 390), (220, 480)], "one", "many1", "possui", (232, 440), "(1,1)", (232, 412), "(1,N)", (232, 472)),
    ([(380, 510), (440, 510), (440, 440), (520, 440)], "one", "many0", "recebe", (446, 478), "(1,1)", (388, 503), "(0,N)", (468, 433)),
    ([(380, 640), (520, 640)], "one", "many0", "agenda", (424, 630), "(1,1)", (388, 657), "(0,N)", (474, 657)),
    ([(380, 688), (470, 688), (470, 900), (520, 900)], "one", "many0", "é atendido", (476, 790), "(1,1)", (388, 682), "(0,N)", (474, 893)),
    ([(980, 590), (910, 590), (910, 440), (840, 440)], "one", "many0", "aplica", (916, 520), "(1,1)", (930, 583), "(0,N)", (848, 433)),
    ([(980, 650), (840, 650)], "one", "many0", "realiza", (880, 674), "(1,1)", (930, 643), "(0,N)", (848, 643)),
    ([(980, 700), (900, 700), (900, 880), (840, 880)], "one", "many0", "atende", (906, 790), "(1,1)", (930, 693), "(0,N)", (848, 873)),
    ([(680, 755), (680, 830)], "opt", "opt", "gera", (692, 798), "(0,1)", (692, 776), "(0,1)", (692, 822)),
    ([(680, 229), (680, 300)], "one", "many0", "é aplicada em", (692, 272), "(1,1)", (692, 250), "(0,N)", (692, 294)),
    ([(840, 1000), (980, 1000)], "one", "many0", "contém", (882, 1024), "(1,1)", (848, 993), "(0,N)", (930, 993)),
]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def box(name, x, y, rows):
    h = HDR + ROW * len(rows)
    out = [f'<g>']
    out.append(f'<rect x="{x}" y="{y}" width="{W_BOX}" height="{h}" rx="6" fill="#ffffff" stroke="{C_BORDER}" stroke-width="1.6"/>')
    out.append(f'<path d="M{x} {y+HDR} V{y+6} a6 6 0 0 1 6 -6 H{x+W_BOX-6} a6 6 0 0 1 6 6 V{y+HDR} Z" fill="{C_HDR}"/>')
    out.append(f'<text x="{x+W_BOX/2}" y="{y+22}" text-anchor="middle" font-size="15" font-weight="700" fill="#ffffff">{esc(name)}</text>')
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
        out.append(f'<text x="{x+TAG_W}" y="{ty}" font-size="13" font-weight="{weight}" fill="{C_TXT}"{deco} xml:space="preserve">{esc(attr)}</text>')
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


def edge(pts, m0, m1, verb, pv, c0, p0, c1, p1):
    d = "M" + " L".join(f"{x} {y}" for x, y in pts)
    out = [f'<path d="{d}" fill="none" stroke="{C_LINE}" stroke-width="1.6" marker-start="url(#{m0})" marker-end="url(#{m1})"/>']
    vw = len(verb) * 7.2 + 10
    out.append(f'<rect x="{pv[0]-4}" y="{pv[1]-13}" width="{vw}" height="18" rx="9" fill="#fdf1e3" stroke="#d9822b" stroke-width="1"/>')
    out.append(f'<text x="{pv[0]+1}" y="{pv[1]}" font-size="12" font-style="italic" fill="#8a4b0f">{esc(verb)}</text>')
    for c, p in ((c0, p0), (c1, p1)):
        out.append(f'<text x="{p[0]}" y="{p[1]}" font-size="12" font-weight="700" fill="#b0261c">{c}</text>')
    return "\n".join(out)


def legend(x, y):
    out = [f'<rect x="{x}" y="{y}" width="320" height="300" rx="6" fill="#f7f9fb" stroke="#c4ccd6"/>',
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
    out.append(f'<text x="{x+20}" y="{yy+80}" font-size="11.5" fill="#55606e">Versão 1: antes da normalização.</text>')
    out.append(f'<text x="{x+20}" y="{yy+97}" font-size="11.5" fill="#55606e">Notação: pé de galinha (crow’s foot).</text>')
    return "\n".join(out)


WIDTH, HEIGHT = 1360, 1360
parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" font-family="Helvetica, Arial, sans-serif">',
         f'<rect width="{WIDTH}" height="{HEIGHT}" fill="#ffffff"/>',
         '<g transform="translate(0,115)">',  # centraliza para o recorte central do sips
         marker_defs(),
         f'<text x="60" y="44" font-size="22" font-weight="700" fill="{C_HDR}">PetCare – Diagrama Entidade-Relacionamento (versão inicial)</text>',
         f'<text x="60" y="64" font-size="13" fill="#55606e">Sistema de Gestão para Clínica Veterinária · modelo lógico</text>']
for e in edges:
    parts.append(edge(*e))
for name, (x, y, rows) in entities.items():
    parts.append(box(name, x, y, rows))
parts.append(legend(60, 780))
parts.append('</g>')
parts.append('</svg>')

with open("DER_PetCare_v1.svg", "w", encoding="utf-8") as f:
    f.write("\n".join(parts))
print("ok")
