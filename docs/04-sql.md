# Experiência Prática IV – SQL (DDL e DML)

Os scripts estão na pasta [`database/`](../database/), com instruções detalhadas em [`database/README.md`](../database/README.md).

## Ambiente

- **SGBD:** MySQL Community Server 8.0 (motor InnoDB, `utf8mb4`).
- **Ferramenta:** MySQL Workbench 8.0.
- **Versão mínima:** 8.0.16, a primeira que aplica as restrições `CHECK`.

## Scripts

| Script | Conteúdo |
|---|---|
| `01_ddl_criacao.sql` | Banco `petcare` e as 12 tabelas, com PK, FK (`RESTRICT`/`CASCADE`), `UNIQUE` e `CHECK` |
| `02_insert_povoamento.sql` | Carga fictícia em ordem hierárquica, dentro de uma transação, com testes de integridade comentados |
| `03_select_consultas.sql` | 5 consultas: prontuário, próximos agendamentos, vacinas a vencer, ranking de veterinários e prescrições |
| `04_update.sql` | 5 atualizações com `WHERE` por chave e `SELECT` de conferência antes e depois |
| `05_delete.sql` | Exclusões controladas, tratando as dependências (filho antes do pai) |

## Regras de integridade em destaque

- **Ordem de INSERT:** domínios → tutor → telefone → animal → veterinário → vacina → agendamento → atendimento → prescrição → aplicação de vacina.
- **ON DELETE RESTRICT** impede excluir registros com dependentes (ex.: tutor com animais, erro 1451).
- **UNIQUE (id_veterinario, data_hora)** impede conflito de agenda.
- **Exclusão lógica:** agendamentos são cancelados (`status = 'Cancelado'`), não apagados.
- **Valores derivados** (espécie, peso atual e próxima dose) são obtidos por JOIN ou cálculo, nunca armazenados.

## Da teoria ao software

A aplicação Flask deste repositório usa o mesmo banco e as mesmas regras:

| Regra do modelo | Onde aparece no sistema |
|---|---|
| Espécie vem da raça (3FN) | Cadastro do animal escolhe só a raça, agrupada por espécie |
| Agendamento obrigatório para atendimento | O atendimento é aberto a partir de um agendamento pendente |
| UNIQUE de agenda | Mensagem "Este veterinário já tem um agendamento neste horário" |
| Próxima dose calculada | Painel e tela de vacinas com alertas de vencidas ou a vencer |
| Peso atual derivado | Ficha do animal mostra o peso do atendimento mais recente |
| Exclusão lógica | Botão "Cancelar" altera o status sem apagar o agendamento |
| Vacina compatível com a espécie | O registro de dose recusa vacina de outra espécie |
