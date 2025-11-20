# Sistema de Gestão para Oficina Mecânica

## 📌 Descrição do Projeto

Este projeto é um **sistema web** para gerenciamento de uma oficina mecânica, permitindo controle completo de:
- Clientes
- Veículos
- Mecânicos
- Serviços
- Peças
- Agendamentos
- Ordens de Serviço

Inclui **dashboard**, **relatórios**, suporte a **modelos 3D** para visualização e **PWA** (Progressive Web App) com cache offline via Service Worker.

---

## 🚀 Tecnologias Utilizadas

- **Backend**: Flask + Flask-SQLAlchemy
- **Banco de Dados**: PostgreSQL
- **Frontend**: HTML5, CSS3, JavaScript
- **Extras**:
  - Service Worker para PWA
  - Modelos 3D (GLTF + BIN)

---

## 📂 Estrutura do Projeto

```
app/
  |   ├──static/
  |   |    ├─ css/
  |   |    |     ├── style.css
  |   |    ├─ models_3d/
  |   |    |     ├── order/
  |   |    |     │   ├── scene.gltf
  |   |    |     ├── user/
  |   |    |     │   ├── scene.gltf
  |   |    |     ├── worker/
  |   |    |     │   ├── scene.gltf
  |   |    |     ├── wrench/
  |   |    |     |   ├── scene.gltf
  |   ├─ templates/
  |   │   ├── agendamento/
  |   │   │   ├── criar.html
  |   │   │   ├── editar.html
  |   │   │   ├── listar.html
  |   │   ├── cliente/
  |   │   │   ├── criar.html
  |   │   │   ├── editar.html
  |   │   │   ├── listar.html
  |   │   ├── mecanico/
  |   |   │   │   ├── criar.html
  |   |   │   │   ├── editar.html
  |   |   │   │   ├── listar.html
  |   │   ├── ordem_de_servico/
  |   |   │   │   ├── criar.html
  |   |   │   │   ├── editar.html
  |   |   │   │   ├── listar.html
  |   │   ├── peca/
  |   |   │   │   ├── criar.html
  |   |   │   │   ├── editar.html
  |   |   │   │   ├── listar.html
  |   │   ├── servico/
  |   │   │   ├── criar.html
  |   |   │   ├── editar.html
  |   |   │   ├── listar.html
  |   │   ├── veiculo/
  |   │   │   ├── criar.html
  |   |   │   ├── editar.html
  |   |   │   ├── listar.html
  |   │   ├── base.html
  |   │   ├── dashboard.html
  |   │   ├── relatorios.html
  │   ├── __init__.py
  │   ├── models.py
  │   ├── routes.py
config.py
requirements.txt
run.py
documents/
```

---

## 🔑 Funcionalidades

- CRUD completo para todas as entidades
- Dashboard com estatísticas
- Relatórios
- Visualização de modelos 3D
- PWA com cache offline

---

## ⚙️ Instalação e Execução Local

### 1. Clonar o repositório

```bash
git clone https://github.com/thales-vaz-sousa/sistema_oficina.git
cd sistema-oficina
```

### 2. Criar ambiente virtual e instalar dependências

```bash
python -m venv venv
source venv/bin/activate  #Linux/Mac
venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### 3. Iniciar e Configurar Banco PostgreSQL

```bash
# Na aplicação pgAdmin criar ou abrir banco
dropdb sistema_oficina --if-exists
createdb sistema_oficina

# Na aplicação pgAdmin executar script SQL ou refazer banco com schemav1.sql
psql -U postgres -d sistema_oficina -f backup.sql

# Em config.py mudar o campo password
password = "sua_senha_aqui"
```

### 4. Rodar aplicação

```bash
python run.py
```
Acesse em: `http://localhost:5000`

---

## 🔒 Configuração

Arquivo `config.py` já está preparado para PostgreSQL. Ajuste usuário, senha e host conforme necessário.

---

## 🖼️ Modelos 3D

Os arquivos GLTF e BIN na pasta `models_3d` permitem visualização interativa de peças e ordens de serviço.

---

## 📱 PWA (Progressive Web App)

O arquivo `sw.js` implementa cache offline para recursos estáticos e modelos 3D, permitindo acesso mesmo sem conexão.

---

## 📊 Dashboard e Relatórios

- Dashboard com estatísticas gerais
- Relatórios para análise de serviços, peças e ordens

---

## ✅ Comandos Rápidos

```bash
# Criar banco
createdb sistema_oficina

# Executar script SQL
psql -U postgres -d sistema_oficina -f backup.sql

# Instalar dependências
pip install -r requirements.txt

# Rodar aplicação
python run.py
```

---

## 📄 Licença

Este projeto é open-source sob a licença MIT.
