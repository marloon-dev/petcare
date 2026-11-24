# PetCare – Banco de Dados para Clínica Veterinária

Projeto acadêmico da disciplina de **Modelagem de Banco de Dados**. Implementa em MySQL o modelo lógico do minimundo PetCare, normalizado até a 3FN, com scripts de criação, carga, consulta, atualização e exclusão de dados.

## 1. Sobre o minimundo

O PetCare centraliza a rotina de uma clínica veterinária de pequeno ou médio porte:

- cadastro de **tutores** (com vários telefones) e de seus **animais**;
- cadastro de **veterinários** e suas especialidades;
- **agendamento** de consultas, retornos, vacinações e procedimentos, sem conflito de horário;
- **atendimento** clínico (prontuário) com **prescrições**;
- controle de **vacinação**, com cálculo da próxima dose.

Ficam fora do escopo: financeiro, estoque, RH, pet shop, internação e portal do tutor.

## 2. Estrutura do banco (12 tabelas)

| Grupo | Tabelas |
|---|---|
| Domínio | `especie`, `raca`, `especialidade` |
| Cadastro | `tutor`, `telefone_tutor`, `animal`, `veterinario`, `vacina` |
| Movimento | `agendamento`, `atendimento`, `prescricao`, `aplicacao_vacina` |

**Regras de integridade principais**

- Todas as PKs são `INT AUTO_INCREMENT`, e todas as FKs têm integridade referencial (InnoDB).
- `ON DELETE RESTRICT` por padrão: não é possível excluir registros com dependentes. Só `telefone_tutor` e `prescricao` usam `CASCADE`.
- `UNIQUE`: CPF do tutor, CRMV, horário por veterinário (`id_veterinario + data_hora`) e um atendimento por agendamento.
- `CHECK`: sexo (`M`/`F`), status do agendamento, tipo de atendimento, tipo de telefone e valores maiores que zero.
- **3FN:** a espécie vem da raça, o animal e o veterinário do atendimento vêm do agendamento, e a próxima dose é calculada (`data_aplicacao + intervalo_reforco_dias`), não armazenada.

## 3. Pré-requisitos

- **MySQL Server 8.0.16 ou superior** (versão mínima que aplica as restrições `CHECK`).
- **MySQL Workbench 8.0** ou outro cliente MySQL (DBeaver, linha de comando `mysql`).
- Um usuário com permissão para criar bancos (ex.: `root` em ambiente local).

## 4. Arquivos do projeto

```
database/
├── 01_ddl_criacao.sql       # cria o banco e as 12 tabelas
├── 02_insert_povoamento.sql # carga de dados de teste
├── 03_select_consultas.sql  # 5 consultas com JOIN, WHERE, ORDER BY e LIMIT
├── 04_update.sql            # 5 atualizações condicionais
├── 05_delete.sql            # exclusões controladas (5 comandos)
└── README.md
```

## 5. Ordem de execução

Os scripts **devem** ser executados nesta ordem, pois cada um depende do anterior:

| Ordem | Script | O que faz |
|---|---|---|
| 1 | `01_ddl_criacao.sql` | Apaga e recria o banco `petcare` com todas as restrições |
| 2 | `02_insert_povoamento.sql` | Insere a carga de teste respeitando a hierarquia das FKs |
| 3 | `03_select_consultas.sql` | Valida a carga com consultas relacionais |
| 4 | `04_update.sql` | Aplica alterações com `WHERE` por chave |
| 5 | `05_delete.sql` | Executa exclusões tratando as dependências antes |

> ⚠️ O script 01 começa com `DROP DATABASE IF EXISTS petcare`. Rodá-lo de novo apaga todos os dados e reinicia o projeto do zero.

### No MySQL Workbench

1. Abra a conexão local (ex.: `127.0.0.1:3306`).
2. Menu **File > Open SQL Script** e abra o `01_ddl_criacao.sql`.
3. Execute o script inteiro com o ícone do raio (**Execute**) ou `Ctrl + Shift + Enter`.
4. Repita os passos 2 e 3 para os scripts 02 a 05, nesta ordem.
5. Clique em **Refresh** no painel *Schemas* para ver as tabelas.

### Pela linha de comando

```bash
mysql -u root -p < 01_ddl_criacao.sql
mysql -u root -p petcare < 02_insert_povoamento.sql
mysql -u root -p petcare < 03_select_consultas.sql
mysql -u root -p petcare < 04_update.sql
mysql -u root -p petcare < 05_delete.sql
```

## 6. Dados de teste

Todos os dados são **fictícios**. A carga inclui 6 tutores, 10 animais (cães, gatos e um coelho), 4 veterinários, 6 vacinas, 15 agendamentos (realizados, cancelados e futuros), 9 atendimentos, 8 prescrições e 11 aplicações de vacina. Também há casos especiais para testar as consultas: animal sem data de nascimento, especialidade sem veterinário e vacinas vencidas.

## 7. Como validar

- Ao final do script 02, um `SELECT ... UNION ALL` mostra a quantidade de registros por tabela.
- Cada consulta do script 03 traz nos comentários o **resultado esperado**.
- Os scripts 04 e 05 exibem um `SELECT` de conferência antes e depois de cada alteração.
- Os scripts 02, 04 e 05 terminam com **testes de integridade comentados**. Retire o comentário de um por vez: todos devem ser **recusados** pelo banco (erros 1062, 1451, 1452 ou 3819).

## 8. Observações

- **Safe Updates:** todos os `UPDATE` e `DELETE` filtram por chave, então funcionam com essa opção do Workbench ativada.
- **Transações:** os scripts 02, 04 e 05 usam `START TRANSACTION` e `COMMIT`. Em caso de erro no meio da execução, rode `ROLLBACK;`.
- **Datas:** as consultas 2 e 3 usam `CURDATE()`, então o resultado varia conforme o dia da execução. Os comentários consideram 24/11/2026.
