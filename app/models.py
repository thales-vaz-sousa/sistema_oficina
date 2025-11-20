from datetime import datetime
from . import db

class Cliente(db.Model):
    __tablename__ = "cliente"
    id_cliente = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    endereco = db.Column(db.String(200), nullable=False)
    data_cadastro = db.Column(db.Date, nullable=False)

    veiculos = db.relationship("Veiculo", back_populates="cliente")

class Veiculo(db.Model):
    __tablename__ = "veiculo"
    id_veiculo = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(8), unique=True, nullable=False)
    marca = db.Column(db.String(50), nullable=False)
    modelo = db.Column(db.String(50), nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    cor = db.Column(db.String(30))
    km_atual = db.Column(db.Integer)
    id_cliente = db.Column(db.Integer, db.ForeignKey("cliente.id_cliente"), nullable=False)

    cliente = db.relationship("Cliente", back_populates="veiculos")
    agendamentos = db.relationship("Agendamento", back_populates="veiculo")
    ordens = db.relationship("OrdemDeServico", back_populates="veiculo")

class Mecanico(db.Model):
    __tablename__ = "mecanico"
    id_mecanico = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    especialidade = db.Column(db.String(50))
    data_admissao = db.Column(db.Date, nullable=False)

    agendamentos = db.relationship("Agendamento", back_populates="mecanico", cascade="all, delete-orphan")
    ordens = db.relationship("OrdemDeServico", back_populates="mecanico", cascade="all, delete-orphan")

class Agendamento(db.Model):
    __tablename__ = "agendamento"
    id_agendamento = db.Column(db.Integer, primary_key=True)
    data_agendamento = db.Column(db.Date, nullable=False)
    hora_agendamento = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    observacoes = db.Column(db.String(200))
    id_veiculo = db.Column(db.Integer, db.ForeignKey("veiculo.id_veiculo"), nullable=False)
    id_mecanico = db.Column(db.Integer, db.ForeignKey("mecanico.id_mecanico"), nullable=False)

    veiculo = db.relationship("Veiculo", back_populates="agendamentos")
    mecanico = db.relationship("Mecanico", back_populates="agendamentos")
    ordens = db.relationship("OrdemDeServico", back_populates="agendamento")

class Servico(db.Model):
    __tablename__ = "servico"
    id_servico = db.Column(db.Integer, primary_key=True)
    nome_servico = db.Column(db.String(50), nullable=False)
    descricao = db.Column(db.String(200))
    preco_base = db.Column(db.Numeric(10,2), nullable=False)
    tempo_estimado = db.Column(db.Integer)

    itens = db.relationship("ItemOrdemServico", back_populates="servico", cascade="all, delete-orphan")

class Peca(db.Model):
    __tablename__ = "peca"
    id_peca = db.Column(db.Integer, primary_key=True)
    nome_peca = db.Column(db.String(50), nullable=False)
    descricao = db.Column(db.String(200))
    preco_custo = db.Column(db.Numeric(10,2), nullable=False)
    preco_venda = db.Column(db.Numeric(10,2), nullable=False)
    estoque_minimo = db.Column(db.Integer)
    estoque_atual = db.Column(db.Integer, nullable=False)

    pecas_os = db.relationship("PecaOrdemServico", back_populates="peca", cascade="all, delete-orphan")

class OrdemDeServico(db.Model):
    __tablename__ = "ordem_de_servico"
    id_ordem_servico = db.Column(db.Integer, primary_key=True)
    numero_os = db.Column(db.String(20), unique=True, nullable=False)
    data_abertura = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    data_conclusao = db.Column(db.DateTime)
    status = db.Column(db.String(20), nullable=False)
    valor_total = db.Column(db.Numeric(10,2))
    observacoes = db.Column(db.String(200))
    id_agendamento = db.Column(db.Integer, db.ForeignKey("agendamento.id_agendamento"))
    id_veiculo = db.Column(db.Integer, db.ForeignKey("veiculo.id_veiculo"), nullable=False)
    id_mecanico = db.Column(db.Integer, db.ForeignKey("mecanico.id_mecanico"), nullable=False)

    agendamento = db.relationship("Agendamento", back_populates="ordens")
    veiculo = db.relationship("Veiculo", back_populates="ordens")
    mecanico = db.relationship("Mecanico", back_populates="ordens")
    itens_servico = db.relationship("ItemOrdemServico", back_populates="ordem", cascade="all, delete-orphan")
    pecas_os = db.relationship("PecaOrdemServico", back_populates="ordem", cascade="all, delete-orphan")

class ItemOrdemServico(db.Model):
    __tablename__ = "item_ordem_servico"
    id_item_os = db.Column(db.Integer, primary_key=True)
    id_ordem_servico = db.Column(db.Integer, db.ForeignKey("ordem_de_servico.id_ordem_servico"))
    id_servico = db.Column(db.Integer, db.ForeignKey("servico.id_servico"))
    quantidade = db.Column(db.Integer, nullable=False)
    preco_unitario = db.Column(db.Numeric(10,2), nullable=False)
    desconto = db.Column(db.Numeric(10,2))
    valor_total = db.Column(db.Numeric(10,2), nullable=False)

    ordem = db.relationship("OrdemDeServico", back_populates="itens_servico")
    servico = db.relationship("Servico", back_populates="itens")

class PecaOrdemServico(db.Model):
    __tablename__ = "peca_ordem_servico"
    id_peca_os = db.Column(db.Integer, primary_key=True)
    id_ordem_servico = db.Column(db.Integer, db.ForeignKey("ordem_de_servico.id_ordem_servico"))
    id_peca = db.Column(db.Integer, db.ForeignKey("peca.id_peca"))
    quantidade = db.Column(db.Integer, nullable=False)
    preco_unitario = db.Column(db.Numeric(10,2), nullable=False)
    valor_total = db.Column(db.Numeric(10,2), nullable=False)

    ordem = db.relationship("OrdemDeServico", back_populates="pecas_os")
    peca = db.relationship("Peca", back_populates="pecas_os")
    