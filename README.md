# 🐾 PetCare – Sistema de Gestão para Clínica Veterinária

Projeto acadêmico da disciplina de **Modelagem de Banco de Dados**. Este repositório reúne todo o percurso, do minimundo ao software funcionando:

1. **Análise do minimundo:** escopo, atores, processos e entidades.
2. **Modelagem conceitual:** DER, relacionamentos e cardinalidades.
3. **Normalização** até a 3FN e projeto lógico.
4. **Implementação em MySQL:** DDL, carga, consultas, atualizações e exclusões.
5. **Aplicação web em Python + Flask** sobre esse banco.

![DER lógico final](docs/img/DER_PetCare_v2_final.png)

## Funcionalidades

- **Painel:** totais, próximos agendamentos e vacinas vencidas ou a vencer em 30 dias.
- **Tutores:** cadastro com validação de CPF, UF e CEP, vários telefones e busca por nome ou CPF.
- **Animais:** cadastro (a espécie vem da raça) e ficha com peso atual, situação vacinal e prontuário completo.
- **Agenda:** novos agendamentos com bloqueio de conflito de horário, filtros por status e cancelamento (exclusão lógica).
- **Atendimento:** registro de queixa, peso, diagnóstico, tratamento e até 3 prescrições, tudo numa única transação.
- **Vacinas:** registro de doses (só aceita vacinas da espécie do animal) e alertas de reforço calculados.

## Estrutura do repositório

```
PetCare/
├── app/                    # aplicação Flask
│   ├── __init__.py         # criação da aplicação e filtros de data/telefone
│   ├── db.py               # acesso ao banco (SQLAlchemy Core + SQL escrito à mão)
│   ├── views.py            # telas e regras de negócio
│   ├── demo.py             # cria um banco SQLite de demonstração a partir dos scripts
│   ├── templates/          # páginas HTML (Jinja)
│   └── static/style.css
├── database/               # scripts SQL (MySQL 8) e instruções de execução
├── docs/                   # documentação das experiências práticas e diagramas
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

São 33 testes que criam um banco SQLite temporário com a carga de teste e verificam telas e regras de negócio: CPF duplicado, conflito de agenda, vacina de outra espécie, transação do atendimento, alertas de reforço e outras.

## Decisões técnicas

- **SQL explícito:** as consultas são escritas à mão (com `JOIN`, `WHERE`, `ORDER BY` e `LIMIT`), como na disciplina, usando parâmetros nomeados para evitar SQL injection.
- **Portabilidade:** cálculos de data (próxima dose e dias restantes) são feitos em Python, sem funções exclusivas do MySQL. Por isso os testes rodam em SQLite.
- **Integridade no banco:** PK, FK, `UNIQUE` e `CHECK` ficam no DDL. A aplicação trata os erros e mostra mensagens claras.
- **Transações:** operações com várias tabelas (tutor e telefones, atendimento e prescrições e status) são confirmadas juntas ou desfeitas juntas.

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

Todos os dados (nomes, CPFs, telefones e endereços) são **fictícios** e servem apenas para teste.
