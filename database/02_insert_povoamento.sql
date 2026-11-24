-- =====================================================================
-- PetCare - Sistema de Gestão para Clínica Veterinária
-- Script 02: povoamento inicial (DML - INSERT)
-- SGBD: MySQL 8.0 | Pré-requisito: executar 01_ddl_criacao.sql
-- ---------------------------------------------------------------------
-- Observações gerais:
-- * Todos os dados são fictícios (nomes, CPFs, telefones e endereços).
-- * Os IDs são informados explicitamente para deixar as chaves
--   estrangeiras legíveis e previsíveis. Em produção, o AUTO_INCREMENT
--   geraria esses valores.
-- * A ordem dos blocos respeita a hierarquia do modelo: primeiro as
--   tabelas independentes (domínios), depois as que dependem delas.
-- * Tudo roda em uma única transação: se algum INSERT violar uma
--   restrição, basta executar ROLLBACK e nada fica gravado pela metade.
-- =====================================================================

USE petcare;
START TRANSACTION;

-- ---------------------------------------------------------------------
-- BLOCO 1: ESPECIE (tabela independente, domínio)
-- Espécies atendidas pela clínica. Base para RACA e VACINA.
-- ---------------------------------------------------------------------
INSERT INTO especie (id_especie, nome) VALUES
  (1, 'Cão'),
  (2, 'Gato'),
  (3, 'Coelho');

-- ---------------------------------------------------------------------
-- BLOCO 2: ESPECIALIDADE (tabela independente, domínio)
-- 'Cardiologia' fica propositalmente sem veterinário, demonstrando
-- a cardinalidade (0,N) do relacionamento com VETERINARIO.
-- ---------------------------------------------------------------------
INSERT INTO especialidade (id_especialidade, nome) VALUES
  (1, 'Clínica Geral'),
  (2, 'Dermatologia'),
  (3, 'Ortopedia'),
  (4, 'Cardiologia');

-- ---------------------------------------------------------------------
-- BLOCO 3: RACA (depende de ESPECIE)
-- Cada raça pertence a uma única espécie (dependência resolvida na 3FN).
-- 'SRD' (sem raça definida) é cadastrada por espécie, garantindo que
-- todo animal tenha uma raça e, por meio dela, uma espécie.
-- ---------------------------------------------------------------------
INSERT INTO raca (id_raca, nome, id_especie) VALUES
  (1,  'SRD',                1),
  (2,  'Labrador Retriever', 1),
  (3,  'Poodle',             1),
  (4,  'Shih Tzu',           1),
  (5,  'Golden Retriever',   1),
  (6,  'SRD',                2),
  (7,  'Siamês',             2),
  (8,  'Persa',              2),
  (9,  'SRD',                3),
  (10, 'Mini Lop',           3);

-- ---------------------------------------------------------------------
-- BLOCO 4: TUTOR (tabela independente)
-- Endereço atomizado (1FN). CPF único (UNIQUE) e apenas dígitos.
-- 'complemento' e 'email' são opcionais (NULL permitido).
-- ---------------------------------------------------------------------
INSERT INTO tutor (id_tutor, nome, cpf, email, logradouro, numero, complemento, bairro, cidade, uf, cep) VALUES
  (1, 'Maria Oliveira',  '10120230340', 'maria.oliveira@email.com', 'Rua das Acácias',        '120',  'Apto 32', 'Vila Mariana', 'São Paulo',    'SP', '04101000'),
  (2, 'Carlos Lima',     '20230340450', 'carlos.lima@email.com',    'Avenida Paulista',       '1500', 'Sala 8',  'Bela Vista',   'São Paulo',    'SP', '01310100'),
  (3, 'Fernanda Rocha',  '30340450560', 'fernanda.rocha@email.com', 'Rua Barão de Jaguara',   '455',  NULL,      'Centro',       'Campinas',     'SP', '13015001'),
  (4, 'João Pereira',    '40450560670', NULL,                       'Rua Coronel Oliveira Lima', '88', NULL,      'Centro',       'Santo André',  'SP', '09010000'),
  (5, 'Juliana Martins', '50560670780', 'juliana.m@email.com',      'Rua Augusta',            '2010', 'Casa 2',  'Jardins',      'São Paulo',    'SP', '01412000'),
  (6, 'Ricardo Santos',  '60670780890', 'ricardo.santos@email.com', 'Rua Voluntários da Pátria', 'S/N', NULL,   'Santana',      'São Paulo',    'SP', '02011000');

-- ---------------------------------------------------------------------
-- BLOCO 5: TELEFONE_TUTOR (depende de TUTOR)
-- Tabela criada na 1FN para eliminar o atributo multivalorado.
-- Tutores 1, 3 e 6 possuem mais de um telefone (relação 1:N).
-- ---------------------------------------------------------------------
INSERT INTO telefone_tutor (id_telefone, numero, tipo, id_tutor) VALUES
  (1, '11987654321', 'Celular',     1),
  (2, '1133334444',  'Residencial', 1),
  (3, '11976543210', 'Celular',     2),
  (4, '19991234567', 'Celular',     3),
  (5, '1932105500',  'Comercial',   3),
  (6, '11965432109', 'Celular',     4),
  (7, '11954321098', 'Celular',     5),
  (8, '11943210987', 'Celular',     6),
  (9, '1145678900',  'Residencial', 6);

-- ---------------------------------------------------------------------
-- BLOCO 6: ANIMAL (depende de TUTOR e RACA)
-- A espécie NÃO é gravada aqui: ela é obtida pela raça (3FN).
-- O peso também não: vem do último atendimento.
-- 'Max' foi resgatado e não tem data de nascimento conhecida (NULL).
-- ---------------------------------------------------------------------
INSERT INTO animal (id_animal, nome, sexo, data_nascimento, id_tutor, id_raca) VALUES
  (1,  'Luna',   'F', '2021-03-10', 1, 2),   -- Labrador (cão)
  (2,  'Nino',   'M', '2022-07-22', 1, 7),   -- Siamês (gato)
  (3,  'Bob',    'M', '2019-11-05', 2, 3),   -- Poodle (cão)
  (4,  'Thor',   'M', '2020-01-15', 3, 5),   -- Golden Retriever (cão)
  (5,  'Mia',    'F', '2023-02-01', 3, 6),   -- SRD (gato)
  (6,  'Rex',    'M', '2018-06-30', 4, 1),   -- SRD (cão)
  (7,  'Simba',  'M', '2021-09-12', 5, 8),   -- Persa (gato)
  (8,  'Mel',    'F', '2024-04-18', 5, 4),   -- Shih Tzu (cão)
  (9,  'Pipoca', 'F', '2025-01-08', 6, 10),  -- Mini Lop (coelho)
  (10, 'Max',    'M', NULL,         6, 1);   -- SRD (cão), resgatado

-- ---------------------------------------------------------------------
-- BLOCO 7: VETERINARIO (depende de ESPECIALIDADE)
-- CRMV único por profissional (UNIQUE).
-- Dois veterinários em Clínica Geral demonstram a relação 1:N.
-- ---------------------------------------------------------------------
INSERT INTO veterinario (id_veterinario, nome, crmv, telefone, email, id_especialidade) VALUES
  (1, 'Dra. Ana Souza',    'CRMV-SP 12345', '11991112222', 'ana.souza@petcare.vet',    1),
  (2, 'Dr. Pedro Almeida', 'CRMV-SP 23456', '11992223333', 'pedro.almeida@petcare.vet', 2),
  (3, 'Dra. Carla Mendes', 'CRMV-SP 34567', '11993334444', 'carla.mendes@petcare.vet',  3),
  (4, 'Dr. Rafael Costa',  'CRMV-SP 45678', '11994445555', NULL,                        1);

-- ---------------------------------------------------------------------
-- BLOCO 8: VACINA (depende de ESPECIE)
-- intervalo_reforco_dias é usado para calcular a próxima dose
-- (valor derivado, não armazenado em APLICACAO_VACINA).
-- ---------------------------------------------------------------------
INSERT INTO vacina (id_vacina, nome, fabricante, intervalo_reforco_dias, id_especie) VALUES
  (1, 'V10 (Polivalente Canina)',  'Zoetis',               365, 1),
  (2, 'Antirrábica Canina',        'Boehringer Ingelheim', 365, 1),
  (3, 'Gripe Canina',              'MSD Saúde Animal',     365, 1),
  (4, 'V4 (Quádrupla Felina)',     'Zoetis',               365, 2),
  (5, 'Antirrábica Felina',        'Boehringer Ingelheim', 365, 2),
  (6, 'Mixomatose',                'Ourofino',             180, 3);

-- ---------------------------------------------------------------------
-- BLOCO 9: AGENDAMENTO (depende de ANIMAL e VETERINARIO)
-- Mistura de status para as consultas futuras:
--   * 'Realizado' (datas passadas) -> geram ATENDIMENTO;
--   * 'Cancelado' (ids 7 e 11)     -> não geram atendimento;
--   * 'Agendado'  (datas futuras)  -> agenda pendente.
-- O id 6 é uma emergência: o agendamento foi criado no momento do
-- encaixe, conforme a regra adotada na normalização (3FN).
-- UNIQUE (id_veterinario, data_hora) impede conflito de horário.
-- ---------------------------------------------------------------------
INSERT INTO agendamento (id_agendamento, data_hora, tipo_atendimento, status, observacoes, id_animal, id_veterinario) VALUES
  (1,  '2026-10-05 09:00:00', 'Consulta',     'Realizado', 'Check-up anual',                         1,  1),
  (2,  '2026-10-05 10:00:00', 'Vacinação',    'Realizado', NULL,                                     3,  1),
  (3,  '2026-10-12 14:00:00', 'Consulta',     'Realizado', 'Tutora relata coceira intensa',          4,  2),
  (4,  '2026-10-20 15:30:00', 'Consulta',     'Realizado', NULL,                                     2,  1),
  (5,  '2026-10-28 11:00:00', 'Procedimento', 'Realizado', 'Animal agressivo, usar focinheira',      6,  3),
  (6,  '2026-11-03 09:30:00', 'Emergência',   'Realizado', 'Encaixe: atendimento sem marcação prévia', 8, 4),
  (7,  '2026-11-05 16:00:00', 'Consulta',     'Cancelado', 'Tutor cancelou por telefone',            3,  2),
  (8,  '2026-11-10 10:30:00', 'Retorno',      'Realizado', 'Retorno da dermatite',                   4,  2),
  (9,  '2026-11-12 08:30:00', 'Vacinação',    'Realizado', NULL,                                     7,  4),
  (10, '2026-11-18 13:00:00', 'Consulta',     'Realizado', NULL,                                     9,  1),
  (11, '2026-11-20 17:00:00', 'Consulta',     'Cancelado', 'Não compareceu',                         5,  1),
  (12, '2026-11-26 09:00:00', 'Consulta',     'Agendado',  'Remarcação da consulta cancelada',       5,  1),
  (13, '2026-11-27 14:30:00', 'Retorno',      'Agendado',  'Reavaliar necessidade de cirurgia',      6,  3),
  (14, '2026-12-02 10:00:00', 'Vacinação',    'Agendado',  'Primeira vacinação após resgate',        10, 4),
  (15, '2026-12-03 11:30:00', 'Consulta',     'Agendado',  'Avaliar coceira nas orelhas',            1,  2);

-- ---------------------------------------------------------------------
-- BLOCO 10: ATENDIMENTO (depende de AGENDAMENTO)
-- Somente agendamentos 'Realizado' possuem atendimento (relação 1:1,
-- garantida por UNIQUE em id_agendamento). O animal e o veterinário
-- são obtidos pelo agendamento, sem repetição de dados (3FN).
-- ---------------------------------------------------------------------
INSERT INTO atendimento (id_atendimento, data_hora_inicio, queixa, peso_aferido, diagnostico, tratamento, observacoes, id_agendamento) VALUES
  (1, '2026-10-05 09:05:00', 'Check-up anual, sem queixas.', 28.40,
      'Animal saudável. Leve acúmulo de tártaro.', 'Orientada escovação dental diária.', NULL, 1),
  (2, '2026-10-05 10:02:00', 'Reforço anual de vacinas.', 7.80,
      'Exame físico sem alterações. Apto para vacinação.', 'Aplicadas V10 e antirrábica.', NULL, 2),
  (3, '2026-10-12 14:10:00', 'Coceira intensa e queda de pelo no dorso há duas semanas.', 32.10,
      'Dermatite alérgica à picada de pulga (DAPP).', 'Corticoide, antipulgas e banho terapêutico.', 'Retorno em 30 dias.', 3),
  (4, '2026-10-20 15:35:00', 'Vômitos ocasionais e apatia há três dias.', 4.20,
      'Gastrite leve.', 'Dieta leve e protetor gástrico.', NULL, 4),
  (5, '2026-10-28 11:15:00', 'Mancando da pata traseira direita.', 24.50,
      'Ruptura parcial do ligamento cruzado cranial.', 'Repouso, anti-inflamatório e analgésico.', 'Avaliar cirurgia no retorno.', 5),
  (6, '2026-11-03 09:32:00', 'Engoliu um brinquedo de borracha.', 5.30,
      'Corpo estranho gástrico, removido por endoscopia.', 'Jejum de 12 horas e alimentação pastosa.', 'Atendimento de emergência.', 6),
  (7, '2026-11-10 10:35:00', 'Retorno da dermatite.', 32.60,
      'Melhora significativa das lesões.', 'Manter antipulgas a cada 12 semanas.', NULL, 8),
  (8, '2026-11-12 08:35:00', 'Vacinação anual.', 4.90,
      'Apto para vacinação.', 'Aplicadas V4 e antirrábica felina.', NULL, 9),
  (9, '2026-11-18 13:05:00', 'Pouco apetite e dentes compridos.', 1.60,
      'Crescimento excessivo dos incisivos.', 'Desgaste dentário e mais feno na dieta.', NULL, 10);

-- ---------------------------------------------------------------------
-- BLOCO 11: PRESCRICAO (depende de ATENDIMENTO)
-- Um atendimento pode ter várias prescrições (atendimento 3 tem três)
-- ou nenhuma (atendimentos 1, 2, 7 e 8), demonstrando a cardinalidade (0,N).
-- ---------------------------------------------------------------------
INSERT INTO prescricao (id_prescricao, medicamento, dosagem, frequencia, duracao_dias, orientacoes, id_atendimento) VALUES
  (1, 'Prednisolona',            '20 mg',      '1 comprimido a cada 24 horas', 7,  'Dar após a refeição.',                    3),
  (2, 'Fluralaner',              '1000 mg',    'Dose única',                   1,  'Repetir a cada 12 semanas.',              3),
  (3, 'Shampoo de clorexidina',  '2%',         'Banho a cada 3 dias',          21, 'Deixar agir 10 minutos antes de enxaguar.', 3),
  (4, 'Omeprazol',               '10 mg',      '1 cápsula a cada 24 horas',    10, 'Em jejum, pela manhã.',                   4),
  (5, 'Meloxicam',               '2 mg',       '1 comprimido a cada 24 horas', 5,  'Junto com a ração.',                      5),
  (6, 'Dipirona',                '500 mg/ml',  '10 gotas a cada 8 horas',      5,  'Somente em caso de dor.',                 5),
  (7, 'Sucralfato',              '200 mg/ml',  '2 ml a cada 8 horas',          7,  '30 minutos antes das refeições.',         6),
  (8, 'Meloxicam',               '0,5 mg/ml',  '0,3 ml a cada 24 horas',       3,  NULL,                                      9);

-- ---------------------------------------------------------------------
-- BLOCO 12: APLICACAO_VACINA (depende de ANIMAL, VACINA e VETERINARIO)
-- Entidade associativa que resolve a relação N:M entre ANIMAL e VACINA.
-- A vacina aplicada é sempre da mesma espécie do animal.
-- Doses antigas foram incluídas para gerar alertas de reforço:
--   * Thor (V10 e antirrábica em 15/12/2025) -> reforço em 15/12/2026;
--   * Nino (V4 em 30/11/2025)                -> reforço em 30/11/2026;
--   * Pipoca (mixomatose em 02/03/2026)      -> reforço vencido em 29/08/2026.
-- ---------------------------------------------------------------------
INSERT INTO aplicacao_vacina (id_aplicacao, data_aplicacao, lote, id_animal, id_vacina, id_veterinario) VALUES
  (1,  '2025-10-03', 'ZT2509A',  1, 1, 1),   -- Luna   - V10
  (2,  '2026-10-05', 'ZT2608B',  3, 1, 1),   -- Bob    - V10
  (3,  '2026-10-05', 'BI2607R',  3, 2, 1),   -- Bob    - Antirrábica Canina
  (4,  '2026-11-12', 'ZT2610F',  7, 4, 4),   -- Simba  - V4
  (5,  '2026-11-12', 'BI2609F',  7, 5, 4),   -- Simba  - Antirrábica Felina
  (6,  '2025-12-15', 'ZT2511C',  4, 1, 1),   -- Thor   - V10
  (7,  '2025-12-15', 'BI2511R',  4, 2, 1),   -- Thor   - Antirrábica Canina
  (8,  '2025-11-30', 'ZT2510F',  2, 4, 1),   -- Nino   - V4
  (9,  '2026-06-20', 'MSD2605G', 6, 3, 4),   -- Rex    - Gripe Canina
  (10, '2026-03-02', 'OF2602M',  9, 6, 1),   -- Pipoca - Mixomatose
  (11, '2026-04-10', 'ZT2603D',  8, 1, 4);   -- Mel    - V10

-- Confirma a carga somente se todos os INSERTs foram executados sem erro.
COMMIT;

-- ---------------------------------------------------------------------
-- Conferência rápida da carga (quantidade de registros por tabela)
-- ---------------------------------------------------------------------
SELECT 'especie' AS tabela, COUNT(*) AS registros FROM especie
UNION ALL SELECT 'especialidade',    COUNT(*) FROM especialidade
UNION ALL SELECT 'raca',             COUNT(*) FROM raca
UNION ALL SELECT 'tutor',            COUNT(*) FROM tutor
UNION ALL SELECT 'telefone_tutor',   COUNT(*) FROM telefone_tutor
UNION ALL SELECT 'animal',           COUNT(*) FROM animal
UNION ALL SELECT 'veterinario',      COUNT(*) FROM veterinario
UNION ALL SELECT 'vacina',           COUNT(*) FROM vacina
UNION ALL SELECT 'agendamento',      COUNT(*) FROM agendamento
UNION ALL SELECT 'atendimento',      COUNT(*) FROM atendimento
UNION ALL SELECT 'prescricao',       COUNT(*) FROM prescricao
UNION ALL SELECT 'aplicacao_vacina', COUNT(*) FROM aplicacao_vacina;

-- ---------------------------------------------------------------------
-- Teste de integridade (opcional): os comandos abaixo DEVEM falhar.
-- Retire o comentário de um por vez para comprovar as restrições.
-- ---------------------------------------------------------------------
-- 1) FK inexistente: tutor 99 não existe -> erro 1452
-- INSERT INTO animal (nome, sexo, id_tutor, id_raca) VALUES ('Fantasma', 'M', 99, 1);
-- 2) CPF duplicado -> erro 1062 (UNIQUE)
-- INSERT INTO tutor (nome, cpf, logradouro, numero, bairro, cidade, uf, cep)
--   VALUES ('Teste', '10120230340', 'Rua A', '1', 'Centro', 'São Paulo', 'SP', '01000000');
-- 3) Conflito de agenda: Dra. Ana já tem horário em 26/11 às 9h -> erro 1062
-- INSERT INTO agendamento (data_hora, tipo_atendimento, id_animal, id_veterinario)
--   VALUES ('2026-11-26 09:00:00', 'Consulta', 3, 1);
-- 4) Valor fora do domínio: sexo 'X' -> erro 3819 (CHECK)
-- INSERT INTO animal (nome, sexo, id_tutor, id_raca) VALUES ('Teste', 'X', 1, 1);
