# Experiência Prática I – Minimundo e análise de dados

## Título

**PetCare – Sistema de Gestão para Clínica Veterinária**

## Ideia central

O PetCare é um sistema de banco de dados feito para clínicas veterinárias de pequeno e médio porte. Ele centraliza o cadastro de tutores e animais, o agendamento de consultas, o histórico clínico e as vacinas. O objetivo é acabar com os registros em papel e as planilhas espalhadas, dando à equipe acesso rápido e confiável às informações de cada paciente.

## Objetivos

1. **Gerenciar** o cadastro de tutores e animais, com dados pessoais, de contato e características de cada paciente.
2. **Organizar** o agendamento de consultas, vacinas e procedimentos por veterinário, data e horário, sem conflitos de agenda.
3. **Registrar** o histórico clínico de cada animal, com diagnósticos, tratamentos, prescrições e vacinas aplicadas.

## Escopo

| Incluso | Excluso |
|---|---|
| Cadastro de tutores (com vários telefones) | Gestão financeira (faturamento, pagamentos, notas fiscais) |
| Cadastro de animais | Controle de estoque e fornecedores |
| Cadastro de veterinários e especialidades | Recursos humanos (folha, escalas, ponto) |
| Agendamento, remarcação e cancelamento | Pet shop e banho e tosa |
| Prontuário clínico (queixa, diagnóstico, tratamento) | Internação |
| Prescrições de medicamentos | Laudos e imagens de exames |
| Controle de vacinas e alertas de reforço | Portal do tutor, app e notificações automáticas |
| Relatórios básicos (histórico, agenda, vacinas a vencer) | Telemedicina e integrações externas |

## Atores

| Perfil | Papel |
|---|---|
| **Recepcionista** | Cadastra tutores e animais, marca, remarca e cancela agendamentos. Não acessa o conteúdo clínico. |
| **Médico veterinário** | Registra atendimentos, diagnósticos, prescrições e vacinas. Consulta o histórico completo. |
| **Auxiliar veterinário** | Registra peso e triagem e anota vacinas sob supervisão. Não emite diagnóstico nem prescrição. |
| **Gestor (administrador)** | Cadastra veterinários e usuários, mantém as tabelas de apoio e consulta relatórios gerenciais. |

## Processos principais

1. **Cadastro e agendamento:** a recepção busca o tutor pelo CPF. Se não existir, cadastra o tutor e o animal. Depois escolhe o veterinário, a data e o horário, e o sistema impede conflitos. O agendamento é criado com status "Agendado".
2. **Atendimento e prescrição:** o veterinário abre o atendimento, consulta o histórico e registra queixa, peso, diagnóstico e tratamento, além de prescrições opcionais. O agendamento passa para "Realizado".
3. **Vacinação:** a dose aplicada é registrada com vacina, data, lote e responsável. O sistema calcula a próxima dose pelo intervalo de reforço da vacina e lista as vacinas a vencer.

## Entidades identificadas

Tutor, Animal, Veterinário, Agendamento, Atendimento (prontuário), Prescrição, Vacina e Aplicação de Vacina.

## Dado x informação (exemplos)

| Dado bruto | Informação | Contexto aplicado |
|---|---|---|
| `12,5` | O cão Thor pesava 12,5 kg em 10/11, 2 kg a menos que na consulta anterior | Unidade, animal, data e comparação com o histórico |
| `15/12/2026` | A antirrábica da gata Mia vence em 22 dias e o tutor deve ser avisado | Animal, vacina, campo "próxima dose" e data atual |
| `8` | A Dra. Ana tem 8 consultas amanhã (agenda cheia) | Veterinário, data, status e capacidade diária |
| `Cancelado` | O tutor cancelou 3 dos últimos 4 agendamentos (75%) | Agrupamento por tutor e período |
| `Dermatite` | Diagnóstico mais frequente em cães em outubro, 40% a mais que em setembro | Agrupamento por espécie e período |

## Dados estruturados x não estruturados

| Dado | Tipo | Motivo |
|---|---|---|
| CPF, data e hora do agendamento, peso, status, lote | Estruturado | Formato fixo, tipo definido e validável |
| Queixa, observações clínicas, tratamento, orientações de uso, observações da recepção | Não estruturado | Texto livre, sem formato previsível (campos `TEXT`) |
