-- =====================================================================
-- PetCare - Sistema de Gestão para Clínica Veterinária
-- Script 04: atualizações condicionais (DML - UPDATE)
-- SGBD: MySQL 8.0 | Pré-requisito: scripts 01 e 02 executados
-- ---------------------------------------------------------------------
-- Boas práticas aplicadas em todos os comandos:
-- * Todo UPDATE tem WHERE filtrando pela chave primária ou por uma
--   chave única (UNIQUE). Isso garante que só o registro desejado seja
--   alterado e é compatível com o modo "Safe Updates" do Workbench.
-- * Antes de cada UPDATE há um SELECT de conferência com o MESMO WHERE,
--   para ver exatamente quais linhas serão afetadas.
-- * Os comandos rodam em uma transação: se o resultado não for o
--   esperado, basta executar ROLLBACK em vez de COMMIT.
-- =====================================================================

USE petcare;
START TRANSACTION;

-- ---------------------------------------------------------------------
-- UPDATE 1: Atualização cadastral do tutor
-- Cenário: o tutor João Pereira (id 4), que não tinha e-mail, informou
-- um e-mail e um complemento de endereço na recepção.
-- Linhas afetadas esperadas: 1.
-- ---------------------------------------------------------------------
SELECT id_tutor, nome, email, complemento
FROM tutor
WHERE id_tutor = 4;                                   -- conferência (antes)

UPDATE tutor
SET email       = 'joao.pereira@email.com',
    complemento = 'Fundos'
WHERE id_tutor = 4;

SELECT id_tutor, nome, email, complemento
FROM tutor
WHERE id_tutor = 4;                                   -- conferência (depois)

-- ---------------------------------------------------------------------
-- UPDATE 2: Remarcação de agendamento
-- Cenário: o retorno do Rex (agendamento 13) foi remarcado de 27/11
-- às 14h30 para 28/11 às 10h. A condição status = 'Agendado' impede
-- alterar por engano um atendimento já realizado ou cancelado.
-- Integridade: se o novo horário já estivesse ocupado para a mesma
-- veterinária, a restrição UNIQUE (id_veterinario, data_hora) recusaria
-- o UPDATE (erro 1062), evitando conflito de agenda.
-- Linhas afetadas esperadas: 1.
-- ---------------------------------------------------------------------
SELECT id_agendamento, data_hora, status, observacoes
FROM agendamento
WHERE id_agendamento = 13 AND status = 'Agendado';    -- conferência (antes)

UPDATE agendamento
SET data_hora   = '2026-11-28 10:00:00',
    observacoes = CONCAT(observacoes, ' | Remarcado a pedido do tutor (era 27/11 14h30).')
WHERE id_agendamento = 13
  AND status = 'Agendado';

SELECT id_agendamento, data_hora, status, observacoes
FROM agendamento
WHERE id_agendamento = 13;                            -- conferência (depois)

-- ---------------------------------------------------------------------
-- UPDATE 3: Cancelamento de agendamento (exclusão lógica)
-- Cenário: a tutora da Luna cancelou a consulta de 03/12
-- (agendamento 15). Em vez de apagar o registro, o status é alterado
-- para 'Cancelado', preservando o histórico.
-- A restrição CHECK só aceita 'Agendado', 'Realizado' ou 'Cancelado'.
-- Linhas afetadas esperadas: 1.
-- ---------------------------------------------------------------------
SELECT id_agendamento, data_hora, status
FROM agendamento
WHERE id_agendamento = 15 AND status = 'Agendado';    -- conferência (antes)

UPDATE agendamento
SET status      = 'Cancelado',
    observacoes = CONCAT(observacoes, ' | Cancelado pela tutora em 24/11/2026.')
WHERE id_agendamento = 15
  AND status = 'Agendado';

SELECT id_agendamento, data_hora, status, observacoes
FROM agendamento
WHERE id_agendamento = 15;                            -- conferência (depois)

-- ---------------------------------------------------------------------
-- UPDATE 4: Mudança de especialidade do veterinário (chave estrangeira)
-- Cenário: o Dr. Rafael Costa concluiu a especialização e passa a atuar
-- em Cardiologia. O filtro usa o CRMV (chave única), e o novo valor da
-- FK é buscado pelo nome da especialidade, sem "número mágico".
-- Integridade: a FK só aceita uma especialidade existente. Se o nome
-- estivesse errado, a subconsulta retornaria NULL e a coluna NOT NULL
-- recusaria a alteração.
-- Linhas afetadas esperadas: 1.
-- ---------------------------------------------------------------------
SELECT v.nome, v.crmv, e.nome AS especialidade
FROM veterinario AS v
    INNER JOIN especialidade AS e ON e.id_especialidade = v.id_especialidade
WHERE v.crmv = 'CRMV-SP 45678';                       -- conferência (antes)

UPDATE veterinario
SET id_especialidade = (SELECT id_especialidade
                        FROM especialidade
                        WHERE nome = 'Cardiologia')
WHERE crmv = 'CRMV-SP 45678';

SELECT v.nome, v.crmv, e.nome AS especialidade
FROM veterinario AS v
    INNER JOIN especialidade AS e ON e.id_especialidade = v.id_especialidade
WHERE v.crmv = 'CRMV-SP 45678';                       -- conferência (depois)

-- ---------------------------------------------------------------------
-- UPDATE 5: Correção de um dado clínico
-- Cenário: a balança estava descalibrada no check-up da Luna
-- (atendimento 1). O peso correto é 28,10 kg.
-- Destaque 3FN: como o peso atual do animal NÃO é armazenado em ANIMAL,
-- basta corrigir o atendimento para que todas as consultas passem a
-- mostrar o valor certo. Não há outra cópia para atualizar.
-- A restrição CHECK (peso_aferido > 0) impede valores inválidos.
-- Linhas afetadas esperadas: 1.
-- ---------------------------------------------------------------------
SELECT id_atendimento, data_hora_inicio, peso_aferido, observacoes
FROM atendimento
WHERE id_atendimento = 1;                             -- conferência (antes)

UPDATE atendimento
SET peso_aferido = 28.10,
    observacoes  = 'Peso corrigido: balança descalibrada no dia do atendimento.'
WHERE id_atendimento = 1;

SELECT id_atendimento, data_hora_inicio, peso_aferido, observacoes
FROM atendimento
WHERE id_atendimento = 1;                             -- conferência (depois)

-- Grava as alterações (use ROLLBACK no lugar se algo saiu diferente).
COMMIT;

-- ---------------------------------------------------------------------
-- Teste de integridade (opcional): os comandos abaixo DEVEM falhar.
-- ---------------------------------------------------------------------
-- 1) FK inexistente: a raça 99 não existe -> erro 1452
-- UPDATE animal SET id_raca = 99 WHERE id_animal = 10;
-- 2) Valor fora do domínio: status inválido -> erro 3819 (CHECK)
-- UPDATE agendamento SET status = 'Pendente' WHERE id_agendamento = 12;
-- 3) CRMV duplicado: já pertence à Dra. Ana Souza -> erro 1062 (UNIQUE)
-- UPDATE veterinario SET crmv = 'CRMV-SP 12345' WHERE id_veterinario = 2;
