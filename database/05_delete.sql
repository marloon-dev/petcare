-- =====================================================================
-- PetCare - Sistema de Gestão para Clínica Veterinária
-- Script 05: exclusões controladas (DML - DELETE)
-- SGBD: MySQL 8.0 | Pré-requisito: scripts 01, 02 e 04 executados
-- ---------------------------------------------------------------------
-- Regras de integridade que orientam as exclusões (definidas no DDL):
-- * ON DELETE RESTRICT (padrão): não é possível excluir um registro
--   "pai" que tenha "filhos" (ex.: tutor com animais, animal com
--   agendamentos). A dependência precisa ser tratada antes.
-- * ON DELETE CASCADE: apenas TELEFONE_TUTOR (ao excluir o tutor) e
--   PRESCRICAO (ao excluir o atendimento) são removidos em cascata.
-- * Registros clínicos (atendimentos e vacinas) não são excluídos, por
--   terem valor legal. Agendamentos com histórico são apenas cancelados
--   (ver UPDATE 3 no script 04).
-- Boas práticas: WHERE pela chave primária ou chave estrangeira, SELECT
-- de conferência antes e depois e uso de transação (ROLLBACK possível).
-- =====================================================================

USE petcare;
START TRANSACTION;

-- ---------------------------------------------------------------------
-- DELETE 1: Remoção de um telefone desatualizado
-- Cenário: a tutora Maria Oliveira (id 1) informou que o telefone
-- residencial foi desligado. Ela continua com o celular, então a regra
-- "todo tutor tem pelo menos um telefone" é mantida.
-- TELEFONE_TUTOR é tabela "filha" sem dependentes: a exclusão é livre.
-- Linhas afetadas esperadas: 1.
-- ---------------------------------------------------------------------
SELECT id_telefone, numero, tipo, id_tutor
FROM telefone_tutor
WHERE id_tutor = 1;                                   -- conferência (antes: 2 telefones)

DELETE FROM telefone_tutor
WHERE id_telefone = 2
  AND id_tutor = 1
  AND tipo = 'Residencial';

SELECT id_telefone, numero, tipo, id_tutor
FROM telefone_tutor
WHERE id_tutor = 1;                                   -- conferência (depois: só o celular)

-- ---------------------------------------------------------------------
-- DELETE 2: Exclusão de uma prescrição lançada por engano
-- Cenário: no atendimento do Rex (id 5), a Dipirona foi registrada por
-- engano, pois a veterinária receitou apenas o Meloxicam. O atendimento
-- e a outra prescrição continuam intactos.
-- Filtro duplo (id_prescricao + id_atendimento) para garantir que a
-- linha removida pertence ao atendimento correto.
-- Linhas afetadas esperadas: 1.
-- ---------------------------------------------------------------------
SELECT id_prescricao, medicamento, dosagem, id_atendimento
FROM prescricao
WHERE id_atendimento = 5;                             -- conferência (antes: 2 prescrições)

DELETE FROM prescricao
WHERE id_prescricao = 6
  AND id_atendimento = 5
  AND medicamento = 'Dipirona';

SELECT id_prescricao, medicamento, dosagem, id_atendimento
FROM prescricao
WHERE id_atendimento = 5;                             -- conferência (depois: só o Meloxicam)

-- ---------------------------------------------------------------------
-- DELETE 3: Limpeza de agendamento cancelado sem histórico
-- Cenário: o agendamento 7 (Bob, 05/11) foi cancelado e nunca gerou
-- atendimento. A clínica decidiu apagar esse registro sem valor.
-- O NOT EXISTS garante que não há atendimento vinculado. Se houvesse,
-- a FK em ATENDIMENTO (RESTRICT) bloquearia a exclusão de qualquer forma.
-- Linhas afetadas esperadas: 1.
-- ---------------------------------------------------------------------
SELECT ag.id_agendamento, ag.data_hora, ag.status, at.id_atendimento
FROM agendamento AS ag
    LEFT JOIN atendimento AS at ON at.id_agendamento = ag.id_agendamento
WHERE ag.id_agendamento = 7;                          -- conferência (antes: sem atendimento)

DELETE FROM agendamento
WHERE id_agendamento = 7
  AND status = 'Cancelado'
  AND NOT EXISTS (SELECT 1
                  FROM atendimento AS at
                  WHERE at.id_agendamento = 7);

SELECT COUNT(*) AS ainda_existe
FROM agendamento
WHERE id_agendamento = 7;                             -- conferência (depois: 0)

-- ---------------------------------------------------------------------
-- DELETE 4: Exclusão de um animal, tratando a dependência antes
-- Cenário: o cão Max (id 10), resgatado, foi adotado por uma família
-- de outra cidade antes da primeira consulta. O cadastro deve ser
-- removido.
-- Integridade: Max tem um agendamento futuro (id 14). Por causa do
-- ON DELETE RESTRICT, excluir o animal direto causaria o erro 1451.
-- Por isso a exclusão segue a ordem: primeiro o "filho" (agendamento),
-- depois o "pai" (animal). Antes, confirmamos que Max não tem
-- atendimentos nem vacinas, ou seja, não há histórico clínico a preservar.
-- Linhas afetadas esperadas: 1 (agendamento) + 1 (animal).
-- ---------------------------------------------------------------------
SELECT
    (SELECT COUNT(*) FROM agendamento      WHERE id_animal = 10)                          AS agendamentos,
    (SELECT COUNT(*) FROM agendamento      WHERE id_animal = 10 AND status = 'Realizado') AS realizados,
    (SELECT COUNT(*) FROM aplicacao_vacina WHERE id_animal = 10)                          AS vacinas;
                                                      -- conferência (antes: 1, 0, 0)

-- 4a) Remove o agendamento pendente (tabela filha)
DELETE FROM agendamento
WHERE id_animal = 10
  AND status = 'Agendado';

-- 4b) Remove o animal (tabela pai), agora sem dependentes
DELETE FROM animal
WHERE id_animal = 10;

SELECT COUNT(*) AS ainda_existe
FROM animal
WHERE id_animal = 10;                                 -- conferência (depois: 0)

-- Grava as exclusões (use ROLLBACK no lugar se algo saiu diferente).
COMMIT;

-- ---------------------------------------------------------------------
-- Teste de integridade (opcional): os comandos abaixo DEVEM falhar,
-- comprovando que o banco impede registros órfãos.
-- ---------------------------------------------------------------------
-- 1) Tutora com animais cadastrados (Luna e Nino) -> erro 1451 (RESTRICT)
-- DELETE FROM tutor WHERE id_tutor = 1;
-- 2) Espécie usada por raças e vacinas -> erro 1451 (RESTRICT)
-- DELETE FROM especie WHERE id_especie = 1;
-- 3) Agendamento que já gerou atendimento -> erro 1451 (RESTRICT)
-- DELETE FROM agendamento WHERE id_agendamento = 1;
