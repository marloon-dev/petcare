-- =====================================================================
-- PetCare - Sistema de Gestão para Clínica Veterinária
-- Script 01: criação do banco e das tabelas (DDL)
-- SGBD: MySQL 8.0 (InnoDB) | Modelo lógico normalizado até a 3FN
-- =====================================================================

DROP DATABASE IF EXISTS petcare;
CREATE DATABASE petcare
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;
USE petcare;

-- ---------------------------------------------------------------------
-- Tabelas de domínio
-- ---------------------------------------------------------------------
CREATE TABLE especie (
  id_especie INT AUTO_INCREMENT PRIMARY KEY,
  nome       VARCHAR(30) NOT NULL,
  CONSTRAINT uk_especie_nome UNIQUE (nome)
) ENGINE = InnoDB;

CREATE TABLE especialidade (
  id_especialidade INT AUTO_INCREMENT PRIMARY KEY,
  nome             VARCHAR(60) NOT NULL,
  CONSTRAINT uk_especialidade_nome UNIQUE (nome)
) ENGINE = InnoDB;

CREATE TABLE raca (
  id_raca    INT AUTO_INCREMENT PRIMARY KEY,
  nome       VARCHAR(50) NOT NULL,
  id_especie INT NOT NULL,
  CONSTRAINT uk_raca_nome_especie UNIQUE (nome, id_especie),
  CONSTRAINT fk_raca_especie FOREIGN KEY (id_especie)
    REFERENCES especie (id_especie) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB;

-- ---------------------------------------------------------------------
-- Tabelas de cadastro
-- ---------------------------------------------------------------------
CREATE TABLE tutor (
  id_tutor    INT AUTO_INCREMENT PRIMARY KEY,
  nome        VARCHAR(100) NOT NULL,
  cpf         CHAR(11)     NOT NULL,
  email       VARCHAR(100),
  logradouro  VARCHAR(120) NOT NULL,
  numero      VARCHAR(10)  NOT NULL,
  complemento VARCHAR(60),
  bairro      VARCHAR(60)  NOT NULL,
  cidade      VARCHAR(60)  NOT NULL,
  uf          CHAR(2)      NOT NULL,
  cep         CHAR(8)      NOT NULL,
  CONSTRAINT uk_tutor_cpf UNIQUE (cpf)
) ENGINE = InnoDB;

CREATE TABLE telefone_tutor (
  id_telefone INT AUTO_INCREMENT PRIMARY KEY,
  numero      VARCHAR(15) NOT NULL,
  tipo        VARCHAR(15) NOT NULL,
  id_tutor    INT NOT NULL,
  CONSTRAINT uk_telefone_tutor UNIQUE (id_tutor, numero),
  CONSTRAINT ck_telefone_tipo CHECK (tipo IN ('Celular', 'Residencial', 'Comercial')),
  CONSTRAINT fk_telefone_tutor FOREIGN KEY (id_tutor)
    REFERENCES tutor (id_tutor) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB;

CREATE TABLE animal (
  id_animal       INT AUTO_INCREMENT PRIMARY KEY,
  nome            VARCHAR(60) NOT NULL,
  sexo            CHAR(1)     NOT NULL,
  data_nascimento DATE,
  id_tutor        INT NOT NULL,
  id_raca         INT NOT NULL,
  CONSTRAINT ck_animal_sexo CHECK (sexo IN ('M', 'F')),
  CONSTRAINT fk_animal_tutor FOREIGN KEY (id_tutor)
    REFERENCES tutor (id_tutor) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_animal_raca FOREIGN KEY (id_raca)
    REFERENCES raca (id_raca) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB;

CREATE TABLE veterinario (
  id_veterinario   INT AUTO_INCREMENT PRIMARY KEY,
  nome             VARCHAR(100) NOT NULL,
  crmv             VARCHAR(15)  NOT NULL,
  telefone         VARCHAR(15)  NOT NULL,
  email            VARCHAR(100),
  id_especialidade INT NOT NULL,
  CONSTRAINT uk_veterinario_crmv UNIQUE (crmv),
  CONSTRAINT fk_veterinario_especialidade FOREIGN KEY (id_especialidade)
    REFERENCES especialidade (id_especialidade) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB;

CREATE TABLE vacina (
  id_vacina              INT AUTO_INCREMENT PRIMARY KEY,
  nome                   VARCHAR(80) NOT NULL,
  fabricante             VARCHAR(80),
  intervalo_reforco_dias INT NOT NULL,
  id_especie             INT NOT NULL,
  CONSTRAINT uk_vacina_nome_fabricante UNIQUE (nome, fabricante),
  CONSTRAINT ck_vacina_intervalo CHECK (intervalo_reforco_dias > 0),
  CONSTRAINT fk_vacina_especie FOREIGN KEY (id_especie)
    REFERENCES especie (id_especie) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB;

-- ---------------------------------------------------------------------
-- Tabelas de movimento
-- ---------------------------------------------------------------------
CREATE TABLE agendamento (
  id_agendamento   INT AUTO_INCREMENT PRIMARY KEY,
  data_hora        DATETIME    NOT NULL,
  tipo_atendimento VARCHAR(30) NOT NULL,
  status           VARCHAR(15) NOT NULL DEFAULT 'Agendado',
  observacoes      TEXT,
  id_animal        INT NOT NULL,
  id_veterinario   INT NOT NULL,
  CONSTRAINT uk_agenda_veterinario_horario UNIQUE (id_veterinario, data_hora),
  CONSTRAINT ck_agendamento_tipo CHECK (tipo_atendimento IN
    ('Consulta', 'Retorno', 'Vacinação', 'Procedimento', 'Emergência')),
  CONSTRAINT ck_agendamento_status CHECK (status IN ('Agendado', 'Realizado', 'Cancelado')),
  CONSTRAINT fk_agendamento_animal FOREIGN KEY (id_animal)
    REFERENCES animal (id_animal) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_agendamento_veterinario FOREIGN KEY (id_veterinario)
    REFERENCES veterinario (id_veterinario) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB;

CREATE TABLE atendimento (
  id_atendimento   INT AUTO_INCREMENT PRIMARY KEY,
  data_hora_inicio DATETIME NOT NULL,
  queixa           TEXT     NOT NULL,
  peso_aferido     DECIMAL(5,2),
  diagnostico      TEXT     NOT NULL,
  tratamento       TEXT,
  observacoes      TEXT,
  id_agendamento   INT NOT NULL,
  CONSTRAINT uk_atendimento_agendamento UNIQUE (id_agendamento),
  CONSTRAINT ck_atendimento_peso CHECK (peso_aferido > 0),
  CONSTRAINT fk_atendimento_agendamento FOREIGN KEY (id_agendamento)
    REFERENCES agendamento (id_agendamento) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB;

CREATE TABLE prescricao (
  id_prescricao  INT AUTO_INCREMENT PRIMARY KEY,
  medicamento    VARCHAR(100) NOT NULL,
  dosagem        VARCHAR(50)  NOT NULL,
  frequencia     VARCHAR(50)  NOT NULL,
  duracao_dias   INT          NOT NULL,
  orientacoes    TEXT,
  id_atendimento INT NOT NULL,
  CONSTRAINT ck_prescricao_duracao CHECK (duracao_dias > 0),
  CONSTRAINT fk_prescricao_atendimento FOREIGN KEY (id_atendimento)
    REFERENCES atendimento (id_atendimento) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB;

CREATE TABLE aplicacao_vacina (
  id_aplicacao   INT AUTO_INCREMENT PRIMARY KEY,
  data_aplicacao DATE        NOT NULL,
  lote           VARCHAR(30) NOT NULL,
  id_animal      INT NOT NULL,
  id_vacina      INT NOT NULL,
  id_veterinario INT NOT NULL,
  CONSTRAINT uk_aplicacao_dose UNIQUE (id_animal, id_vacina, data_aplicacao),
  CONSTRAINT fk_aplicacao_animal FOREIGN KEY (id_animal)
    REFERENCES animal (id_animal) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_aplicacao_vacina FOREIGN KEY (id_vacina)
    REFERENCES vacina (id_vacina) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_aplicacao_veterinario FOREIGN KEY (id_veterinario)
    REFERENCES veterinario (id_veterinario) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB;
