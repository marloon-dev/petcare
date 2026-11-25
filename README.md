<p align="center">
  <img src="app/static/img/logo.png" alt="Logo do PetCare" width="200">
</p>

<h1 align="center">PetCare – Sistema de Gestão para Clínica Veterinária</h1>

<p align="center">
  Tutores, animais, consultas e vacinas em um só lugar.<br>
  Do modelo de dados ao software funcionando.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9%2B-0B6B5A?style=flat-square" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/Flask-3.1-0B6B5A?style=flat-square" alt="Flask 3.1">
  <img src="https://img.shields.io/badge/MySQL-8.0.16%2B-2E7D32?style=flat-square" alt="MySQL 8.0.16+">
  <img src="https://img.shields.io/badge/testes-40%20passando-2E7D32?style=flat-square" alt="40 testes passando">
  <img src="https://img.shields.io/badge/licen%C3%A7a-MIT-F4B400?style=flat-square" alt="Licença MIT">
</p>

![Visão geral do PetCare](docs/img/telas/visao-geral.png)

## Sobre o projeto

Projeto acadêmico da disciplina de **Modelagem de Banco de Dados**. O repositório reúne todo o percurso:

1. **Análise do minimundo:** escopo, atores, processos e entidades.
2. **Modelagem conceitual:** DER, relacionamentos e cardinalidades.
3. **Normalização** até a 3FN e projeto lógico.
4. **Implementação em MySQL:** DDL, carga, consultas, atualizações e exclusões.
5. **Aplicação web em Python + Flask** sobre esse banco, com interface própria.

## Funcionalidades

| Tela | O que faz |
|---|---|
| **Visão geral** | Saudação conforme o horário, totais da clínica, próximos atendimentos e vacinas vencidas ou a vencer em 30 dias |
| **Busca geral** | Barra no topo que encontra tutores (por nome ou CPF, com ou sem pontuação) e animais |
| **Agenda** | Filtros com contagem por status, bloqueio de conflito de horário, atender e cancelar (exclusão lógica, com confirmação) |
| **Atendimento** | Queixa, peso, diagnóstico, tratamento e até 3 prescrições, gravados numa única transação |
| **Tutores** | Cadastro com validação de CPF, UF e CEP, vários telefones e ficha com contatos e animais |
| **Animais** | Cadastro (a espécie vem da raça) e ficha com idade, peso atual, situação vacinal e prontuário em linha do tempo |
| **Vacinas** | Registro de doses (só aceita vacina da espécie do animal) e alertas de reforço calculados |

## Telas

<table>
  <tr>
    <td width="50%"><img src="docs/img/telas/agenda.png" alt="Agenda"><p align="center"><b>Agenda</b></p></td>
    <td width="50%"><img src="docs/img/telas/vacinas.png" alt="Vacinas"><p align="center"><b>Vacinas</b></p></td>
  </tr>
  <tr>
    <td width="50%"><img src="docs/img/telas/ficha-animal.png" alt="Ficha do animal"><p align="center"><b>Ficha do animal e prontuário</b></p></td>
    <td width="50%"><img src="docs/img/telas/novo-tutor.png" alt="Cadastro de tutor"><p align="center"><b>Cadastro de tutor</b></p></td>
  </tr>
</table>

<p align="center">
  <img src="docs/img/telas/celular-visao-geral.png" alt="Visão geral no celular" width="260">
  &nbsp;&nbsp;
  <img src="docs/img/telas/celular-agenda.png" alt="Agenda no celular" width="260">
  <br><b>No celular</b>
</p>

## Design

A interface parte do logo do PetCare: um cão e um gato formando um coração em volta da cruz de cuidado. A ideia é passar acolhimento sem perder a clareza de um sistema de trabalho.

### Paleta

| Cor | Hex | Uso |
|---|---|---|
| ![](https://img.shields.io/badge/-%20%20%20%20-0B6B5A?style=flat-square) Verde petróleo | `#0B6B5A` | Barra lateral, botões principais, links |
| ![](https://img.shields.io/badge/-%20%20%20%20-2E7D32?style=flat-square) Verde folha | `#2E7D32` | Situação "em dia", status "Realizado" |
| ![](https://img.shields.io/badge/-%20%20%20%20-A7D7C7?style=flat-square) Menta | `#A7D7C7` | Destaques suaves, fundos de ícones |
| ![](https://img.shields.io/badge/-%20%20%20%20-FDF7EB?style=flat-square) Creme | `#FDF7EB` | Fundo das páginas |
| ![](https://img.shields.io/badge/-%20%20%20%20-FF7B6E?style=flat-square) Coral | `#FF7B6E` | Vacina vencida, cancelar |
| ![](https://img.shields.io/badge/-%20%20%20%20-F4B400?style=flat-square) Âmbar | `#F4B400` | Vacina a vencer |

Coral e âmbar aparecem como fundo das etiquetas. O texto delas usa tons mais escuros das mesmas cores, para manter boa leitura.

### Tipografia e componentes

- **Fonte:** [Nunito](https://fonts.google.com/specimen/Nunito), arredondada como o nome no logo. Sem internet, o sistema usa a fonte padrão do aparelho.
- **Ícones:** desenhados em SVG dentro das páginas, no mesmo traço, sem depender de bibliotecas.
- **Avatares:** 🐶 🐱 🐰 conforme a espécie (o banco não guarda fotos). Os tutores aparecem com as iniciais do nome.
- **Etiquetas de situação:** cor e texto juntos ("Vencida há 88 dias", "Vence em 5 dias"), para não depender só da cor.

### Boas práticas de UI/UX aplicadas

- **Hierarquia clara:** cada tela tem título, uma frase de contexto e uma ação principal em destaque.
- **Responsivo:** no celular o menu vira uma barra fixa no rodapé, e as tabelas viram cartões empilhados, sem rolagem lateral.
- **Formulários:** campos agrupados por seção, obrigatórios marcados com `*`, exemplos dentro dos campos, datas limitadas (sem agendar no passado nem registrar vacina no futuro) e prescrições extras recolhidas.
- **Prevenção de erros:** cancelar um agendamento pede confirmação, e os erros do banco (CPF repetido, horário ocupado) viram mensagens em português.
- **Formato brasileiro:** datas por extenso, peso com vírgula (`32,60 kg`) e idade calculada (`6 anos`).
- **Estados vazios:** listas sem resultados mostram um ícone e uma explicação, em vez de uma tabela em branco.
- **Acessibilidade:** navegação pelo teclado com foco visível, link "Pular para o conteúdo", página atual marcada no menu e respeito à preferência de reduzir animações.
- **Honestidade da interface:** não há botões sem função. Login e notificações ficaram de fora porque não fazem parte do escopo do banco.

## Modelo de dados

![DER lógico final](docs/img/DER_PetCare_v2_final.png)

São 12 tabelas normalizadas até a 3FN. A espécie vem da raça, o animal e o veterinário do atendimento vêm do agendamento, e a próxima dose de vacina é calculada, não armazenada. Detalhes em [docs/03-normalizacao.md](docs/03-normalizacao.md).

## Estrutura do repositório

```
PetCare/
├── app/                    # aplicação Flask
│   ├── __init__.py         # criação da aplicação e filtros (datas, idade, peso, telefone)
│   ├── db.py               # acesso ao banco (SQLAlchemy Core + SQL escrito à mão)
│   ├── views.py            # telas, busca e regras de negócio
│   ├── demo.py             # cria um banco SQLite de demonstração a partir dos scripts
│   ├── templates/          # páginas HTML (Jinja) e macros de ícones e avatares
│   └── static/
│       ├── style.css       # identidade visual e layout responsivo
│       └── img/            # logo, símbolo e ícone da aba
├── database/               # scripts SQL (MySQL 8) e instruções de execução
├── docs/                   # experiências práticas, diagramas e capturas de tela
├── tests/                  # testes automatizados (pytest)
├── run.py                  # ponto de entrada (flask --app run ...)
├── requirements.txt
├── .env.example
└── LICENSE                 # licença MIT
```

## Como executar

### Pré-requisitos

- Python 3.9 ou superior
- MySQL 8.0.16 ou superior (opcional: dá para testar sem MySQL, veja a opção B)

### 1. Instalar as dependências

```bash
git clone https://github.com/marloon-dev/petcare.git
cd petcare
python3 -m venv .venv
source .venv/bin/activate        # no Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

### 2A. Com MySQL (recomendado)

1. Execute os scripts `database/01_ddl_criacao.sql` e `database/02_insert_povoamento.sql` no MySQL Workbench (detalhes em [`database/README.md`](database/README.md)).
2. No arquivo `.env`, ajuste a `DATABASE_URL` com seu usuário e senha:
   ```
   DATABASE_URL=mysql+pymysql://root:SUA_SENHA@127.0.0.1:3306/petcare?charset=utf8mb4
   ```

### 2B. Sem MySQL (demonstração com SQLite)

```bash
flask --app run criar-demo
```

Depois coloque no `.env` a linha `DATABASE_URL=sqlite:///` seguida do caminho que o comando mostrar.

### 3. Iniciar

```bash
flask --app run run --debug
```

Acesse **http://127.0.0.1:5000**. No macOS, se a porta 5000 estiver ocupada pelo AirPlay, use `--port 5050`.

## Testes

```bash
python -m pytest
```

São 40 testes que criam um banco SQLite temporário com a carga de teste e verificam telas e regras de negócio: CPF duplicado, conflito de agenda, vacina de outra espécie, transação do atendimento, alertas de reforço, busca geral, idade, datas por extenso e contagem da agenda.

## Decisões técnicas

- **SQL explícito:** as consultas são escritas à mão (com `JOIN`, `WHERE`, `ORDER BY` e `LIMIT`), como na disciplina, usando parâmetros nomeados para evitar SQL injection.
- **Portabilidade:** cálculos de data (próxima dose, dias restantes e idade) são feitos em Python, sem funções exclusivas do MySQL. Por isso os testes rodam em SQLite.
- **Integridade no banco:** PK, FK, `UNIQUE` e `CHECK` ficam no DDL. A aplicação trata os erros e mostra mensagens claras.
- **Transações:** operações com várias tabelas (tutor e telefones, atendimento e prescrições e status) são confirmadas juntas ou desfeitas juntas.
- **Sem build de front-end:** HTML gerado no servidor (Jinja) e um único arquivo CSS, sem frameworks. A página carrega rápido e o código é fácil de ler.

## Documentação

| Documento | Conteúdo |
|---|---|
| [docs/01-minimundo.md](docs/01-minimundo.md) | Minimundo, escopo, atores, processos, dado x informação |
| [docs/02-modelo-conceitual.md](docs/02-modelo-conceitual.md) | DER inicial e final, relacionamentos, suposições e desafios |
| [docs/03-normalizacao.md](docs/03-normalizacao.md) | Auditoria 1FN, 2FN e 3FN e modelo lógico final |
| [docs/04-sql.md](docs/04-sql.md) | Scripts SQL e ligação entre o modelo e o software |
| [database/README.md](database/README.md) | Como executar os scripts no MySQL |

## Licença

Distribuído sob a licença MIT. Veja o arquivo [LICENSE](LICENSE).

---

<p align="center">Todos os dados (nomes, CPFs, telefones e endereços) são <b>fictícios</b> e servem apenas para teste.</p>
