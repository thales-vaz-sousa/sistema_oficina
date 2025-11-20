/* Tabela: Cliente */

CREATE TABLE cliente (
id_cliente SERIAL 		PRIMARY KEY,
nome VARCHAR(50) 		NOT NULL,
cpf VARCHAR(14) 		UNIQUE NOT NULL,
telefone VARCHAR(20) 	NOT NULL,
email VARCHAR(150) 		UNIQUE NOT NULL,
endereco VARCHAR(200) 	NOT NULL,
data_cadastro DATE 		NOT NULL);

/* Tabela: veiculo */

CREATE TABLE veiculo (
id_veiculo SERIAL 	PRIMARY KEY,
placa VARCHAR(8) 	UNIQUE NOT NULL,
marca VARCHAR(50) 	NOT NULL,
modelo VARCHAR(50) 	NOT NULL,
ano INT 			NOT NULL,
cor VARCHAR(30),
km_atual INT,
id_cliente INT 		NOT NULL,
FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente));

/* Tabela: mecanico */

CREATE TABLE mecanico (
id_mecanico SERIAL 		PRIMARY KEY,
nome VARCHAR(50) 		NOT NULL,
cpf VARCHAR(14) 		UNIQUE NOT NULL,
telefone VARCHAR(20) 	NOT NULL,
especialidade VARCHAR(50),
data_admissao DATE 		NOT NULL);

/* Tabela: agendamento */ 

CREATE TABLE agendamento (
id_agendamento SERIAL PRIMARY KEY,
data_agendamento DATE 	NOT NULL,
hora_agendamento TIME 	NOT NULL,
status VARCHAR(20) 		NOT NULL,
observacoes VARCHAR(50),
id_veiculo INT 			NOT NULL,
id_mecanico INT 		NOT NULL,
FOREIGN KEY (id_veiculo) REFERENCES veiculo(id_veiculo),
FOREIGN KEY (id_mecanico) REFERENCES mecanico(id_mecanico));

/* Tabela: servico */ 

CREATE TABLE servico (
id_servico SERIAL 			PRIMARY KEY,
nome_servico VARCHAR(50) 	NOT NULL,
descricao VARCHAR(50),
preco_base DECIMAL(10, 2) 	NOT NULL,
tempo_estimado INT);

-- Tabela: peca
CREATE TABLE peca (
 id_peca SERIAL 			PRIMARY KEY,
 nome_peca VARCHAR(50) 		NOT NULL,
 descricao VARCHAR(50),
 preco_custo DECIMAL(10, 2) NOT NULL,
 preco_venda DECIMAL(10, 2) NOT NULL,
 estoque_minimo INT,
 estoque_atual INT 			NOT NULL);

/* Tabela: ordem_de_servico */ 

CREATE TABLE ordem_de_servico (
id_ordem_servico SERIAL 	PRIMARY KEY,
numero_os VARCHAR(20) 		UNIQUE NOT NULL,
data_abertura TIMESTAMP 	NOT NULL,
data_conclusao TIMESTAMP,
status VARCHAR(20) 			NOT NULL,
valor_total DECIMAL(10,2),
observacoes VARCHAR(50),
id_agendamento INT,
id_veiculo INT 				NOT NULL,
id_mecanico INT 			NOT NULL,
FOREIGN KEY (id_agendamento) REFERENCES agendamento(id_agendamento),
FOREIGN KEY (id_veiculo) REFERENCES veiculo(id_veiculo),
FOREIGN KEY (id_mecanico) REFERENCES mecanico(id_mecanico));

/* Tabela: item_ordem_servico (Serviços realizados na OS) */

CREATE TABLE item_ordem_servico (
id_item_os SERIAL 				PRIMARY KEY,
id_ordem_servico INT 			NOT NULL,
id_servico INT 					NOT NULL,
quantidade INT 					NOT NULL,
preco_unitario DECIMAL(10,2) 	NOT NULL,
desconto DECIMAL(10,2),
valor_total DECIMAL(10,2) 		NOT NULL,
FOREIGN KEY (id_ordem_servico) REFERENCES ordem_de_servico(id_ordem_servico),
FOREIGN KEY (id_servico) REFERENCES servico(id_servico));

/* Tabela: peca_ordem_servico (Peças utilizadas na OS) */

CREATE TABLE peca_ordem_servico (
id_peca_os SERIAL PRIMARY KEY,
id_ordem_servico INT NOT NULL,
id_peca INT NOT NULL,
quantidade INT NOT NULL,
preco_unitario DECIMAL(10, 2) NOT NULL,
valor_total DECIMAL(10, 2) NOT NULL,
FOREIGN KEY (id_ordem_servico) REFERENCES ordem_de_servico(id_ordem_servico),
FOREIGN KEY (id_peca) REFERENCES peca(id_peca));

/* DADOS INSERIDOS NAS TABELAS */

/* 1. Inserindo dados na tabela cliente (3 cadastros) */ 

INSERT INTO cliente (nome, cpf, telefone, email, endereco, data_cadastro) VALUES
('Ana Silva', '111.111.111-11', '(11) 98765-4321', 'ana.silva@email.com', 'Rua das Flores, 100, São Paulo - SP', '2024-01-15'),
('Bruno Costa', '222.222.222-22', '(21) 99887-7665', 'bruno.costa@email.com', 'Avenida Principal, 500, Rio de Janeiro - RJ', '2023-11-20'),
('Carla Souza', '333.333.333-33', '(31) 97654-3210', 'carla.souza@email.com', 'Rua da Paz, 30, Belo Horizonte - MG', '2024-05-01');

Select * From Cliente;

/* 2. Inserindo dados na tabela mecanico (3 cadastros) */
INSERT INTO mecanico (nome, cpf, telefone, especialidade, data_admissao) VALUES
('Daniel Pereira', '444.444.444-44', '(11) 91234-5678', 'Motor e Câmbio', '2022-03-10'),
('Eduarda Lima', '555.555.555-55', '(21) 92345-6789', 'Elétrica e Injeção', '2023-01-25'),
('Felipe Santos', '666.666.666-66', '(31) 93456-7890', 'Suspensão e Freios', '2021-08-05');

/* 3. Inserindo dados na tabela servico (3 cadastros) */
INSERT INTO servico (nome_servico, descricao, preco_base, tempo_estimado) VALUES
('Troca de Óleo', 'Substituição de óleo e filtro', 80.00, 60),
('Revisão Completa', 'Check-up geral do veículo', 250.00, 180),
('Alinhamento e Balanceamento', 'Ajuste de direção e rodas', 120.00, 90);

/* 4. Inserindo dados na tabela peca (3 cadastros) */
INSERT INTO peca (nome_peca, descricao, preco_custo, preco_venda, estoque_minimo, estoque_atual) VALUES
('Filtro de Óleo', 'Filtro de óleo universal', 15.00, 30.00, 10, 25),
('Pastilha de Freio', 'Pastilha de freio dianteira', 50.00, 100.00, 5, 15),
('Vela de Ignição', 'Vela de ignição padrão', 10.00, 25.00, 20, 40);

/* 5. Inserindo dados na tabela veiculo (3 cadastros) */ 

INSERT INTO veiculo (placa, marca, modelo, ano, cor, km_atual, id_cliente) VALUES
('ABC1A23', 'Fiat', 'Uno', 2010, 'Vermelho', 150000, 1),
('XYZ9B87', 'Chevrolet', 'Onix', 2022, 'Prata', 25000, 2),
('DEF4C56', 'Ford', 'Ka', 2018, 'Preto', 75000, 3);

-- 6. Inserindo dados na tabela agendamento (3 cadastros)

INSERT INTO agendamento (data_agendamento, hora_agendamento, status, observacoes, id_veiculo, id_mecanico) VALUES
('2025-12-01', '09:00:00', 'Confirmado', 'Troca de óleo urgente', 1, 1),
('2025-12-02', '14:30:00', 'Pendente', 'Revisão antes de viagem', 2, 2),
('2025-12-03', '10:00:00', 'Confirmado', 'Alinhamento de rotina', 3, 3);

-- 7. Inserindo dados na tabela ordem_de_servico (3 cadastros)

INSERT INTO ordem_de_servico (numero_os, data_abertura, data_conclusao, status, valor_total, observacoes, id_agendamento, id_veiculo, id_mecanico) VALUES
('OS-2025-001', '2025-12-01 09:00:00', '2025-12-01 10:30:00', 'Concluída', 110.00, 'Serviço concluído no prazo', 1, 1, 1),
('OS-2025-002', '2025-12-02 14:30:00', NULL, 'Em Andamento', NULL, 'Aguardando aprovação do orçamento', 2, 2, 2),
('OS-2025-003', '2025-12-03 10:00:00', '2025-12-03 11:30:00', 'Concluída', 120.00, 'Alinhamento e balanceamento ok', 3, 3, 3);

-- 8. Inserindo dados na tabela item_ordem_servico (3 cadastros)

INSERT INTO item_ordem_servico (id_ordem_servico, id_servico, quantidade, preco_unitario, desconto, valor_total) VALUES
(1, 1, 1, 80.00, 0.00, 80.00), -- OS-001: Troca de Óleo
(2, 2, 1, 250.00, 0.00, 250.00), -- OS-002: Revisão Completa
(3, 3, 1, 120.00, 0.00, 120.00); -- OS-003: Alinhamento e Balanceamento

-- 9. Inserindo dados na tabela peca_ordem_servico (3 cadastros)

INSERT INTO peca_ordem_servico (id_ordem_servico, id_peca, quantidade, preco_unitario, valor_total) VALUES
(1, 1, 1, 30.00, 30.00), -- OS-001: Filtro de Óleo
(2, 2, 2, 100.00, 200.00), -- OS-002: Pastilha de Freio (2 unidades)
(3, 3, 4, 25.00, 100.00); -- OS-003: Vela de Ignição (4 unidades)

-- Atualizando o valor_total da OS-002 (Revisão Completa + 2 Pastilhas de Freio)
UPDATE ordem_de_servico SET valor_total = 250.00 + 200.00 WHERE id_ordem_servico = 2;
-- O valor total da OS-001 já estava correto (80.00 + 30.00 = 110.00)
-- O valor total da OS-003 já estava correto (120.00 + 100.00 = 220.00)
UPDATE ordem_de_servico SET valor_total = 220.00 WHERE id_ordem_servico = 3;
-- O valor total da OS-001 já estava correto (80.00 + 30.00 = 110.00)
-- O valor total da OS-003 já estava correto (120.00 + 100.00 = 220.00)
UPDATE ordem_de_servico SET valor_total = 110.00 WHERE id_ordem_servico = 1;