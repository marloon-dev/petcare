-- =====================================================================
-- PetCare - Sistema de Gestão para Clínica Veterinária
-- Script 03: consultas exploratórias (DML - SELECT)
-- SGBD: MySQL 8.0 | Pré-requisito: scripts 01 e 02 executados
-- ---------------------------------------------------------------------
-- Data de referência: as consultas 2 e 3 usam CURDATE() (data atual).
-- Os comentários "Resultado esperado" consideram a execução em
-- 24/11/2026, data em que a carga de teste foi montada.
-- =====================================================================

USE petcare;

-- ---------------------------------------------------------------------
-- CONSULTA 1: Histórico clínico de um animal (prontuário)
-- Objetivo: listar os atendimentos do cão "Thor" com espécie, raça,
-- veterinário responsável, diagnóstico e peso aferido.
-- Técnicas: INNER JOIN em 6 tabelas, WHERE, ORDER BY DESC, LIMIT.
-- Destaque 3FN: a espécie vem de RACA, e o animal e o veterinário vêm
-- de AGENDAMENTO (ATENDIMENTO guarda apenas id_agendamento).
-- Resultado esperado: 2 linhas (retorno em 10/11 e consulta em 12/10).
-- ---------------------------------------------------------------------
SELECT
    an.nome                    AS animal,
    es.nome                    AS especie,
    ra.nome                    AS raca,
    at.data_hora_inicio        AS data_atendimento,
    ag.tipo_atendimento,
    ve.nome                    AS veterinario,
    at.diagnostico,
    at.peso_aferido            AS peso_kg
FROM atendimento AS at
    INNER JOIN agendamento AS ag ON ag.id_agendamento = at.id_agendamento
    INNER JOIN animal      AS an ON an.id_animal      = ag.id_animal
    INNER JOIN raca        AS ra ON ra.id_raca        = an.id_raca
    INNER JOIN especie     AS es ON es.id_especie     = ra.id_especie
    INNER JOIN veterinario AS ve ON ve.id_veterinario = ag.id_veterinario
WHERE an.nome = 'Thor'
ORDER BY at.data_hora_inicio DESC
LIMIT 10;

-- ---------------------------------------------------------------------
-- CONSULTA 2: Próximos agendamentos com contato do tutor
-- Objetivo: montar a lista de confirmação da recepção com os 5 próximos
-- compromissos, trazendo o celular do tutor.
-- Técnicas: INNER JOIN, LEFT JOIN com condição no ON (o tutor aparece
-- mesmo sem celular cadastrado), WHERE com status e data, ORDER BY, LIMIT.
-- Resultado esperado: 4 linhas (Mia 26/11, Rex 27/11, Max 02/12,
-- Luna 03/12). Os agendamentos cancelados não aparecem.
-- ---------------------------------------------------------------------
SELECT
    ag.data_hora,
    ag.tipo_atendimento,
    an.nome           AS animal,
    tu.nome           AS tutor,
    tel.numero        AS celular_tutor,
    ve.nome           AS veterinario,
    ag.observacoes
FROM agendamento AS ag
    INNER JOIN animal         AS an  ON an.id_animal      = ag.id_animal
    INNER JOIN tutor          AS tu  ON tu.id_tutor       = an.id_tutor
    INNER JOIN veterinario    AS ve  ON ve.id_veterinario = ag.id_veterinario
    LEFT  JOIN telefone_tutor AS tel ON tel.id_tutor      = tu.id_tutor
                                    AND tel.tipo          = 'Celular'
WHERE ag.status = 'Agendado'
  AND ag.data_hora >= CURDATE()
ORDER BY ag.data_hora ASC
LIMIT 5;

-- ---------------------------------------------------------------------
-- CONSULTA 3: Vacinas vencidas ou que vencem nos próximos 30 dias
-- Objetivo: gerar a lista de reforços para a recepção avisar os tutores.
-- A próxima dose NÃO é armazenada (atributo derivado removido na 3FN):
-- ela é calculada como data_aplicacao + intervalo_reforco_dias.
-- Considera só a dose mais recente de cada vacina por animal (NOT EXISTS).
-- Técnicas: 4 INNER JOINs, cálculo de datas (DATE_ADD, DATEDIFF),
-- subconsulta correlacionada, WHERE, ORDER BY, LIMIT.
-- Resultado esperado: 5 linhas, em ordem de urgência:
--   Pipoca/Mixomatose e Luna/V10 (vencidas), Nino/V4 (30/11),
--   Thor/V10 e Thor/Antirrábica (15/12).
-- ---------------------------------------------------------------------
SELECT
    an.nome                                                     AS animal,
    tu.nome                                                     AS tutor,
    va.nome                                                     AS vacina,
    av.data_aplicacao                                           AS ultima_dose,
    DATE_ADD(av.data_aplicacao, INTERVAL va.intervalo_reforco_dias DAY) AS proxima_dose,
    DATEDIFF(DATE_ADD(av.data_aplicacao, INTERVAL va.intervalo_reforco_dias DAY),
             CURDATE())                                         AS dias_restantes
FROM aplicacao_vacina AS av
    INNER JOIN vacina AS va ON va.id_vacina = av.id_vacina
    INNER JOIN animal AS an ON an.id_animal = av.id_animal
    INNER JOIN tutor  AS tu ON tu.id_tutor  = an.id_tutor
WHERE DATE_ADD(av.data_aplicacao, INTERVAL va.intervalo_reforco_dias DAY)
          <= DATE_ADD(CURDATE(), INTERVAL 30 DAY)
  AND NOT EXISTS (                 -- ignora doses que já tiveram reforço
        SELECT 1
        FROM aplicacao_vacina AS posterior
        WHERE posterior.id_animal      = av.id_animal
          AND posterior.id_vacina      = av.id_vacina
          AND posterior.data_aplicacao > av.data_aplicacao
      )
ORDER BY proxima_dose ASC
LIMIT 10;

-- ---------------------------------------------------------------------
-- CONSULTA 4: Ranking de veterinários por atendimentos realizados
-- Objetivo: relatório gerencial de produtividade no período de
-- outubro e novembro de 2026.
-- Técnicas: INNER JOIN, WHERE com intervalo de datas (BETWEEN),
-- agregação (COUNT, COUNT DISTINCT, GROUP BY), ORDER BY, LIMIT (top 3).
-- Resultado esperado: Dra. Ana Souza (4), Dr. Pedro Almeida (2),
-- Dr. Rafael Costa (2).
-- ---------------------------------------------------------------------
SELECT
    ve.nome                            AS veterinario,
    esp.nome                           AS especialidade,
    COUNT(at.id_atendimento)           AS total_atendimentos,
    COUNT(DISTINCT ag.id_animal)       AS animais_atendidos
FROM atendimento AS at
    INNER JOIN agendamento   AS ag  ON ag.id_agendamento    = at.id_agendamento
    INNER JOIN veterinario   AS ve  ON ve.id_veterinario    = ag.id_veterinario
    INNER JOIN especialidade AS esp ON esp.id_especialidade = ve.id_especialidade
WHERE at.data_hora_inicio BETWEEN '2026-10-01 00:00:00' AND '2026-11-30 23:59:59'
GROUP BY ve.id_veterinario, ve.nome, esp.nome
ORDER BY total_atendimentos DESC, ve.nome ASC
LIMIT 3;

-- ---------------------------------------------------------------------
-- CONSULTA 5: Prescrições de anti-inflamatórios e analgésicos
-- Objetivo: rastrear quais animais receberam medicamentos que exigem
-- acompanhamento, com o tutor e o veterinário responsável.
-- Técnicas: 5 INNER JOINs, WHERE com IN, ORDER BY em duas colunas, LIMIT.
-- Resultado esperado: 4 linhas (Rex com Dipirona e Meloxicam,
-- Pipoca com Meloxicam e Thor com Prednisolona).
-- ---------------------------------------------------------------------
SELECT
    an.nome                AS animal,
    tu.nome                AS tutor,
    pr.medicamento,
    pr.dosagem,
    pr.frequencia,
    pr.duracao_dias,
    ve.nome                AS prescrito_por,
    DATE(at.data_hora_inicio) AS data_prescricao
FROM prescricao AS pr
    INNER JOIN atendimento AS at ON at.id_atendimento = pr.id_atendimento
    INNER JOIN agendamento AS ag ON ag.id_agendamento = at.id_agendamento
    INNER JOIN animal      AS an ON an.id_animal      = ag.id_animal
    INNER JOIN tutor       AS tu ON tu.id_tutor       = an.id_tutor
    INNER JOIN veterinario AS ve ON ve.id_veterinario = ag.id_veterinario
WHERE pr.medicamento IN ('Meloxicam', 'Dipirona', 'Prednisolona')
ORDER BY an.nome ASC, pr.medicamento ASC
LIMIT 10;
