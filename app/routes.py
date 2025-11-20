from flask import render_template, request, redirect, url_for, flash, current_app, send_from_directory
from app import db
from app.models import Cliente, Veiculo, Mecanico, Servico, Peca, Agendamento, OrdemDeServico, ItemOrdemServico, PecaOrdemServico
from datetime import datetime
from sqlalchemy.orm import joinedload
from sqlalchemy import cast, Date, extract

#================================
# ROTAS DA APLICAÇÃO
#================================

def init_app(app):

    @app.route('/sw.js')
    def service_worker():
        # serve the static/sw.js at site root so the SW scope can be '/'
        return send_from_directory(current_app.static_folder, 'sw.js')

    @app.route('/')
    @app.route('/dashboard')
    def home():
        try:
            hoje = datetime.now().date()

            # Próximos agendamentos (data >= hoje)
            proximos_agendamentos = db.session.query(Agendamento).options(
                joinedload(Agendamento.veiculo).joinedload(Veiculo.cliente),
                joinedload(Agendamento.mecanico)
            ).filter(
                Agendamento.data_agendamento >= hoje
            ).order_by(
                Agendamento.data_agendamento, Agendamento.hora_agendamento
            ).limit(5).all()

            # Ordens em andamento (status relevantes)
            ordens_andamento = db.session.query(OrdemDeServico).options(
                joinedload(OrdemDeServico.veiculo).joinedload(Veiculo.cliente),
                joinedload(OrdemDeServico.mecanico)
            ).filter(
                OrdemDeServico.status.in_(['Em Andamento', 'Pendente'])
            ).order_by(
                OrdemDeServico.data_abertura.desc()
            ).limit(5).all()

            # contagens para os cards
            c = db.session.query(Cliente).count()
            v = db.session.query(Veiculo).count()
            m = db.session.query(Mecanico).count()
            s = db.session.query(Servico).count()
            p = db.session.query(Peca).count()
            a = db.session.query(Agendamento).count()
            o = db.session.query(OrdemDeServico).count()

            # Séries mensais (últimos 6 meses) — contagem de ordens e agendamentos
            months = []
            orders_series = []
            agend_series = []
            today = datetime.now().date()

            # Estabelece o mês final como o maior entre hoje e as últimas datas presentes no banco
            latest_ordem = db.session.query(OrdemDeServico).order_by(OrdemDeServico.data_abertura.desc()).first()
            latest_agend = db.session.query(Agendamento).order_by(Agendamento.data_agendamento.desc()).first()

            end_date = today
            if latest_ordem and latest_ordem.data_abertura:
                d = latest_ordem.data_abertura
                if isinstance(d, datetime):
                    d = d.date()
                if d > end_date:
                    end_date = d
            if latest_agend and latest_agend.data_agendamento:
                d = latest_agend.data_agendamento
                if isinstance(d, datetime):
                    d = d.date()
                if d > end_date:
                    end_date = d

            year = end_date.year
            month = end_date.month

            def month_start_end(y, m):
                start = datetime(y, m, 1).date()
                if m == 12:
                    end = datetime(y + 1, 1, 1).date()
                else:
                    end = datetime(y, m + 1, 1).date()
                return start, end

            # gerar últimos 6 meses (do mais antigo ao mais recente)
            for i in range(5, -1, -1):
                ym = month - i
                yy = year
                # ajustar ano/mês quando menor que 1
                while ym <= 0:
                    ym += 12
                    yy -= 1
                start, end = month_start_end(yy, ym)
                label = f"{start.strftime('%b %Y')}"
                months.append(label)

                # contar ordens usando year/month (mais resiliente a tipos datetime/timestamp)
                orders_count = db.session.query(OrdemDeServico).filter(
                    extract('year', OrdemDeServico.data_abertura) == yy,
                    extract('month', OrdemDeServico.data_abertura) == ym
                ).count()

                agend_count = db.session.query(Agendamento).filter(
                    extract('year', Agendamento.data_agendamento) == yy,
                    extract('month', Agendamento.data_agendamento) == ym
                ).count()

                orders_series.append(orders_count)
                agend_series.append(agend_count)

            # DEBUG: logar meses e séries para confirmar o que será renderizado
            print("DEBUG dashboard months:", months)
            print("DEBUG orders_series:", orders_series)
            print("DEBUG agend_series:", agend_series)
 
            return render_template('dashboard.html',
                                    clientes=c, veiculos=v, mecanicos=m,
                                    servicos=s, pecas=p, agendamentos=a, ordens=o,
                                    proximos_agendamentos=proximos_agendamentos,
                                    ordens_andamento=ordens_andamento,
                                    months_labels=months,
                                    orders_series=orders_series,
                                    agend_series=agend_series)
        except Exception as e:
            print("Erro na dashboard:", e)
            return render_template('dashboard.html',
                                    clientes=0, veiculos=0, mecanicos=0,
                                    servicos=0, pecas=0, agendamentos=0, ordens=0,
                                    proximos_agendamentos=[], ordens_andamento=[],
                                    months_labels=[], orders_series=[], agend_series=[])

    #================================
    # CLIENTES
    #================================

    @app.route('/clientes')
    def clientes_listar():
        clientes = Cliente.query.order_by(Cliente.nome).all()
        return render_template('cliente/listar.html', clientes=clientes)

    @app.route('/clientes/criar', methods=['GET', 'POST'])
    def clientes_criar():
        if request.method == 'POST':
            try:
                with app.app_context():
                    cliente = Cliente(
                        nome=request.form['nome'],
                        cpf=request.form['cpf'],
                        telefone=request.form['telefone'],
                        email=request.form['email'],
                        endereco=request.form['endereco'],
                        data_cadastro=datetime.strptime(request.form['data_cadastro'], '%Y-%m-%d').date() 
                        if request.form.get('data_cadastro') else datetime.utcnow().date()
                    )
                    db.session.add(cliente)
                    db.session.commit()
                flash("Cliente cadastrado com sucesso!", "success")
                return redirect(url_for('clientes_listar'))
            except Exception as e:
                db.session.rollback()
                flash(f"Erro ao cadastrar cliente: {str(e)}", "danger")
        
        return render_template('cliente/criar.html')

    @app.route('/clientes/editar/<int:id>', methods=['GET', 'POST'])
    def clientes_editar(id):
        cliente = Cliente.query.get_or_404(id)
        if request.method == 'POST':
            cliente.nome = request.form.get('nome')
            cliente.cpf = request.form.get('cpf')
            cliente.telefone = request.form.get('telefone')
            cliente.email = request.form.get('email')
            cliente.endereco = request.form.get('endereco')
            # data_cadastro opcional: converter se necessário
            data = request.form.get('data_cadastro')
            if data:
                cliente.data_cadastro = datetime.fromisoformat(data).date()
            try:
                db.session.commit()   # <- garante persistência
                flash('Cliente atualizado.', 'success')
            except Exception as e:
                db.session.rollback()
                current_app.logger.exception('Erro ao atualizar cliente')
                flash('Erro ao salvar alterações.', 'danger')
            # PRG: redireciona para a listagem para forçar novo SELECT
            return redirect(url_for('clientes_listar'))
        # GET: renderiza o formulário
        return render_template('cliente/editar.html', cliente=cliente)

    @app.route('/clientes/excluir/<int:id>')
    def clientes_excluir(id):
        try:
            with app.app_context():
                cliente = db.session.query(Cliente).get(id)
                if cliente:
                    db.session.delete(cliente)
                    db.session.commit()
                    flash("Cliente removido com sucesso!", "danger")
                else:
                    flash("Cliente não encontrado!", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao excluir cliente: {str(e)}", "danger")
        
        return redirect(url_for('clientes_listar'))

    #================================
    # VEÍCULOS
    #================================

    @app.route('/veiculos')
    def veiculos_listar():
        veiculos = Veiculo.query.order_by(Veiculo.placa).all()
        return render_template('veiculo/listar.html', veiculos=veiculos)

    @app.route('/veiculos/criar', methods=['GET', 'POST'])
    def veiculos_criar():
        with app.app_context():
            clientes = db.session.query(Cliente).all()
            
        if request.method == 'POST':
            try:
                with app.app_context():
                    veiculo = Veiculo(
                        placa=request.form['placa'],
                        marca=request.form['marca'],
                        modelo=request.form['modelo'],
                        ano=int(request.form['ano']) if request.form.get('ano') else None,
                        cor=request.form.get('cor'),
                        km_atual=int(request.form['km_atual']) if request.form.get('km_atual') else None,
                        id_cliente=int(request.form['id_cliente'])
                    )
                    db.session.add(veiculo)
                    db.session.commit()
                flash("Veículo cadastrado com sucesso!", "success")
                return redirect(url_for('veiculos_listar'))
            except Exception as e:
                db.session.rollback()
                flash(f"Erro ao cadastrar veículo: {str(e)}", "danger")
        
        return render_template('veiculo/criar.html', clientes=clientes)

    @app.route('/veiculos/editar/<int:id>', methods=['GET', 'POST'])
    def veiculos_editar(id):
        veiculo = Veiculo.query.get_or_404(id)
        if request.method == 'POST':
            veiculo.placa = request.form.get('placa')
            veiculo.marca = request.form.get('marca')
            veiculo.modelo = request.form.get('modelo')
            veiculo.ano = request.form.get('ano') or None
            veiculo.cor = request.form.get('cor')
            veiculo.km_atual = request.form.get('km_atual') or None
            veiculo.id_cliente = request.form.get('id_cliente')
            try:
                db.session.commit()
                flash('Veículo atualizado.', 'success')
            except Exception:
                db.session.rollback()
                current_app.logger.exception('Erro ao atualizar veículo')
                flash('Erro ao salvar.', 'danger')
            return redirect(url_for('veiculos_listar'))
        clientes = Cliente.query.order_by(Cliente.nome).all()
        return render_template('veiculo/editar.html', veiculo=veiculo, clientes=clientes)

    @app.route('/veiculos/excluir/<int:id>')
    def veiculos_excluir(id):
        try:
            with app.app_context():
                veiculo = db.session.query(Veiculo).get(id)
                if veiculo:
                    db.session.delete(veiculo)
                    db.session.commit()
                    flash("Veículo excluído com sucesso!", "danger")
                else:
                    flash("Veículo não encontrado!", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao excluir veículo: {str(e)}", "danger")
        
        return redirect(url_for('veiculos_listar'))

    #================================
    # MECÂNICOS
    #================================

    @app.route('/mecanicos')
    def mecanicos_listar():
        with app.app_context():
            mecanicos = db.session.query(Mecanico).all()
        return render_template('mecanico/listar.html', mecanicos=mecanicos)

    @app.route('/mecanicos/criar', methods=['GET', 'POST'])
    def mecanicos_criar():
        if request.method == 'POST':
            try:
                with app.app_context():
                    mecanico = Mecanico(
                        nome=request.form['nome'],
                        cpf=request.form['cpf'],
                        telefone=request.form['telefone'],
                        especialidade=request.form.get('especialidade'),
                        data_admissao=datetime.strptime(request.form['data_admissao'], '%Y-%m-%d').date()
                    )
                    db.session.add(mecanico)
                    db.session.commit()
                flash("Mecânico cadastrado com sucesso!", "success")
                return redirect(url_for('mecanicos_listar'))
            except Exception as e:
                db.session.rollback()
                flash(f"Erro ao cadastrar mecânico: {str(e)}", "danger")
        
        return render_template('mecanico/criar.html')

    @app.route('/mecanicos/editar/<int:id>', methods=['GET', 'POST'])
    def mecanicos_editar(id):
        # carregar objeto diretamente (GET ou POST)
        mecanico = Mecanico.query.get_or_404(id)

        if request.method == 'POST':
            try:
                mecanico.nome = request.form.get('nome')
                mecanico.cpf = request.form.get('cpf')
                mecanico.telefone = request.form.get('telefone')
                mecanico.especialidade = request.form.get('especialidade')
                data_adm = request.form.get('data_admissao')
                mecanico.data_admissao = datetime.strptime(data_adm, '%Y-%m-%d').date() if data_adm else None

                db.session.commit()
                current_app.logger.info(f"Mecânico {id} atualizado.")
                flash("Mecânico atualizado com sucesso!", "success")
                return redirect(url_for('mecanicos_listar'))
            except Exception as e:
                db.session.rollback()
                current_app.logger.exception("Erro ao atualizar mecânico")
                flash("Erro ao atualizar mecânico.", "danger")

        return render_template('mecanico/editar.html', mecanico=mecanico)

    @app.route('/mecanicos/excluir/<int:id>')
    def mecanicos_excluir(id):
        try:
            with app.app_context():
                mecanico = db.session.query(Mecanico).get(id)
                if mecanico:
                    db.session.delete(mecanico)
                    db.session.commit()
                    flash("Mecânico removido com sucesso!", "danger")
                else:
                    flash("Mecânico não encontrado!", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao excluir mecânico: {str(e)}", "danger")
        
        return redirect(url_for('mecanicos_listar'))

    #================================
    # SERVIÇOS
    #================================

    @app.route('/servicos')
    def servicos_listar():
        with app.app_context():
            servicos = db.session.query(Servico).all()
        return render_template('servico/listar.html', servicos=servicos)

    @app.route('/servicos/criar', methods=['GET', 'POST'])
    def servicos_criar():
        if request.method == 'POST':
            try:
                with app.app_context():
                    servico = Servico(
                        nome_servico=request.form['nome_servico'],
                        descricao=request.form.get('descricao'),
                        preco_base=float(request.form['preco_base']),
                        tempo_estimado=int(request.form['tempo_estimado']) if request.form.get('tempo_estimado') else None
                    )
                    db.session.add(servico)
                    db.session.commit()
                flash("Serviço cadastrado com sucesso!", "success")
                return redirect(url_for('servicos_listar'))
            except Exception as e:
                db.session.rollback()
                flash(f"Erro ao cadastrar serviço: {str(e)}", "danger")
        
        return render_template('servico/criar.html')

    @app.route('/servicos/editar/<int:id>', methods=['GET', 'POST'])
    def servicos_editar(id):
        servico = Servico.query.get_or_404(id)

        if request.method == 'POST':
            try:
                servico.nome_servico = request.form.get('nome_servico')
                servico.descricao = request.form.get('descricao') or None
                servico.preco_base = float(request.form.get('preco_base') or 0)
                tempo = request.form.get('tempo_estimado')
                servico.tempo_estimado = int(tempo) if tempo else None

                db.session.commit()
                flash("Serviço atualizado com sucesso!", "success")
                return redirect(url_for('servicos_listar'))
            except Exception:
                db.session.rollback()
                current_app.logger.exception("Erro ao atualizar serviço")
                flash("Erro ao atualizar serviço.", "danger")

        return render_template('servico/editar.html', servico=servico)

    @app.route('/servicos/excluir/<int:id>')
    def servicos_excluir(id):
        try:
            with app.app_context():
                servico = db.session.query(Servico).get(id)
                if servico:
                    db.session.delete(servico)
                    db.session.commit()
                    flash("Serviço removido com sucesso!", "danger")
                else:
                    flash("Serviço não encontrado!", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao excluir serviço: {str(e)}", "danger")
        
        return redirect(url_for('servicos_listar'))

    #================================
    # PEÇAS
    #================================

    @app.route('/pecas')
    def pecas_listar():
        # lista sempre atualizada direto do DB
        pecas = Peca.query.order_by(Peca.nome_peca).all()
        return render_template('peca/listar.html', pecas=pecas)

    @app.route('/pecas/criar', methods=['GET', 'POST'])
    def pecas_criar():
        if request.method == 'POST':
            try:
                with app.app_context():
                    peca = Peca(
                        nome_peca=request.form['nome_peca'],
                        descricao=request.form.get('descricao'),
                        preco_custo=float(request.form['preco_custo']),
                        preco_venda=float(request.form['preco_venda']),
                        estoque_minimo=int(request.form.get('estoque_minimo')) if request.form.get('estoque_minimo') else None,
                        estoque_atual=int(request.form['estoque_atual'])
                    )
                    db.session.add(peca)
                    db.session.commit()
                flash("Peça cadastrada com sucesso!", "success")
                return redirect(url_for('pecas_listar'))
            except Exception as e:
                db.session.rollback()
                flash(f"Erro ao cadastrar peça: {str(e)}", "danger")
        
        return render_template('peca/criar.html')

    @app.route('/pecas/editar/<int:id>', methods=['GET', 'POST'])
    def pecas_editar(id):
        peca = Peca.query.get_or_404(id)

        if request.method == 'POST':
            try:
                peca.nome_peca = request.form.get('nome_peca')
                peca.descricao = request.form.get('descricao') or None
                preco_custo = request.form.get('preco_custo')
                preco_venda = request.form.get('preco_venda')
                estoque_min = request.form.get('estoque_minimo')
                estoque_atual = request.form.get('estoque_atual')

                peca.preco_custo = float(preco_custo) if preco_custo not in (None, '') else 0.0
                peca.preco_venda = float(preco_venda) if preco_venda not in (None, '') else 0.0
                peca.estoque_minimo = int(estoque_min) if estoque_min not in (None, '') else None
                peca.estoque_atual = int(estoque_atual) if estoque_atual not in (None, '') else 0

                db.session.commit()
                flash("Peça atualizada com sucesso!", "success")
                return redirect(url_for('pecas_listar'))
            except Exception as e:
                db.session.rollback()
                current_app.logger.exception("Erro ao atualizar peça")
                flash(f"Erro ao atualizar peça: {e}", "danger")

        return render_template('peca/editar.html', peca=peca)

    @app.route('/pecas/excluir/<int:id>')
    def pecas_excluir(id):
        try:
            with app.app_context():
                peca = db.session.query(Peca).get(id)
                if peca:
                    db.session.delete(peca)
                    db.session.commit()
                    flash("Peça removida com sucesso!", "danger")
                else:
                    flash("Peça não encontrada!", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao excluir peça: {str(e)}", "danger")
        
        return redirect(url_for('pecas_listar'))

    #================================
    # AGENDAMENTOS
    #================================

    @app.route('/agendamentos')
    def agendamentos_listar():
        agendamentos = Agendamento.query.order_by(Agendamento.data_agendamento.desc(), Agendamento.hora_agendamento.desc()).all()
        return render_template('agendamento/listar.html', agendamentos=agendamentos)

    @app.route('/agendamentos/criar', methods=['GET', 'POST'])
    def agendamentos_criar():
        with app.app_context():
            veiculos = db.session.query(Veiculo).all()
            mecanicos = db.session.query(Mecanico).all()
            
        if request.method == 'POST':
            try:
                with app.app_context():
                    agendamento = Agendamento(
                        data_agendamento=datetime.strptime(request.form['data_agendamento'], '%Y-%m-%d').date(),
                        hora_agendamento=datetime.strptime(request.form['hora_agendamento'], '%H:%M').time(),
                        status=request.form['status'],
                        observacoes=request.form.get('observacoes'),
                        id_veiculo=int(request.form['id_veiculo']),
                        id_mecanico=int(request.form['id_mecanico'])
                    )
                    db.session.add(agendamento)
                    db.session.commit()
                flash("Agendamento criado com sucesso!", "success")
                return redirect(url_for('agendamentos_listar'))
            except Exception as e:
                db.session.rollback()
                flash(f"Erro ao criar agendamento: {str(e)}", "danger")
        
        return render_template('agendamento/criar.html', veiculos=veiculos, mecanicos=mecanicos)

    @app.route('/agendamentos/editar/<int:id>', methods=['GET', 'POST'])
    def agendamentos_editar(id):
        agendamento = Agendamento.query.get_or_404(id)
        veiculos = Veiculo.query.order_by(Veiculo.placa).all()
        mecanicos = Mecanico.query.order_by(Mecanico.nome).all()

        if request.method == 'POST':
            try:
                data_str = request.form.get('data_agendamento')
                hora_str = request.form.get('hora_agendamento')

                agendamento.data_agendamento = datetime.strptime(data_str, '%Y-%m-%d').date() if data_str else None

                # aceitar HH:MM ou HH:MM:SS
                if hora_str:
                    try:
                        agendamento.hora_agendamento = datetime.strptime(hora_str, '%H:%M').time()
                    except ValueError:
                        agendamento.hora_agendamento = datetime.strptime(hora_str, '%H:%M:%S').time()

                agendamento.status = request.form.get('status') or None
                agendamento.observacoes = request.form.get('observacoes') or None
                agendamento.id_veiculo = int(request.form.get('id_veiculo')) if request.form.get('id_veiculo') else None
                agendamento.id_mecanico = int(request.form.get('id_mecanico')) if request.form.get('id_mecanico') else None

                db.session.commit()
                flash("Agendamento atualizado com sucesso.", "success")
                return redirect(url_for('agendamentos_listar'))
            except Exception as e:
                db.session.rollback()
                current_app.logger.exception("Erro ao atualizar agendamento")
                flash(f"Erro ao atualizar agendamento: {e}", "danger")

        return render_template('agendamento/editar.html', agendamento=agendamento, veiculos=veiculos, mecanicos=mecanicos)

    @app.route('/agendamentos/excluir/<int:id>')
    def agendamentos_excluir(id):
        try:
            with app.app_context():
                agendamento = db.session.query(Agendamento).get(id)
                if agendamento:
                    db.session.delete(agendamento)
                    db.session.commit()
                    flash("Agendamento removido com sucesso!", "danger")
                else:
                    flash("Agendamento não encontrado!", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao excluir agendamento: {str(e)}", "danger")
        
        return redirect(url_for('agendamentos_listar'))

    #================================
    # ORDENS DE SERVIÇO
    #================================

    @app.route('/ordens')
    def ordens_listar():
        with app.app_context():
            # CORREÇÃO: Usar joinedload para veículo e mecânico
            ordens = db.session.query(OrdemDeServico).options(
                joinedload(OrdemDeServico.veiculo),
                joinedload(OrdemDeServico.mecanico)
            ).all()
        return render_template('ordem_de_servico/listar.html', ordens=ordens)

    @app.route('/ordens/criar', methods=['GET', 'POST'])
    def ordens_criar():
        with app.app_context():
            veiculos = db.session.query(Veiculo).all()
            mecanicos = db.session.query(Mecanico).all()
            # CORREÇÃO: Carregar agendamentos com veiculo
            agendamentos = db.session.query(Agendamento).options(
                joinedload(Agendamento.veiculo)
            ).all()
            servicos = db.session.query(Servico).all()
            pecas = db.session.query(Peca).all()
            
        if request.method == 'POST':
            try:
                with app.app_context():
                    ordem = OrdemDeServico(
                        numero_os=request.form['numero_os'],
                        data_abertura=datetime.strptime(request.form['data_abertura'], '%Y-%m-%dT%H:%M'),
                        status=request.form['status'],
                        observacoes=request.form.get('observacoes'),
                        id_agendamento=int(request.form['id_agendamento']) if request.form.get('id_agendamento') else None,
                        id_veiculo=int(request.form['id_veiculo']),
                        id_mecanico=int(request.form['id_mecanico'])
                    )
                    db.session.add(ordem)
                    db.session.flush()  # Para obter o ID sem commit
                    
                    valor_total = 0
                    
                    # Processar serviços
                    servicos_ids = request.form.getlist('servicos_ids[]')
                    servicos_qtd = request.form.getlist('servicos_qtd[]')
                    
                    for i, servico_id in enumerate(servicos_ids):
                        if servico_id:  # Só processa se foi selecionado um serviço
                            servico = db.session.query(Servico).get(int(servico_id))
                            quantidade = int(servicos_qtd[i])
                            preco_unitario = servico.preco_base
                            total_item = preco_unitario * quantidade
                            
                            item = ItemOrdemServico(
                                id_ordem_servico=ordem.id_ordem_servico,
                                id_servico=servico.id_servico,
                                quantidade=quantidade,
                                preco_unitario=preco_unitario,
                                valor_total=total_item
                            )
                            db.session.add(item)
                            valor_total += total_item
                    
                    # Processar peças
                    pecas_ids = request.form.getlist('pecas_ids[]')
                    pecas_qtd = request.form.getlist('pecas_qtd[]')
                    
                    for i, peca_id in enumerate(pecas_ids):
                        if peca_id:  # Só processa se foi selecionada uma peça
                            peca = db.session.query(Peca).get(int(peca_id))
                            quantidade = int(pecas_qtd[i])
                            preco_unitario = peca.preco_venda
                            total_item = preco_unitario * quantidade
                            
                            item_peca = PecaOrdemServico(
                                id_ordem_servico=ordem.id_ordem_servico,
                                id_peca=peca.id_peca,
                                quantidade=quantidade,
                                preco_unitario=preco_unitario,
                                valor_total=total_item
                            )
                            db.session.add(item_peca)
                            valor_total += total_item
                    
                    # Atualizar valor total da OS
                    ordem.valor_total = valor_total
                    db.session.commit()
                    
                    flash("Ordem de Serviço criada com sucesso!", "success")
                    return redirect(url_for('ordens_listar'))
                    
            except Exception as e:
                db.session.rollback()
                flash(f"Erro ao criar ordem de serviço: {str(e)}", "danger")
        
        return render_template('ordem_de_servico/criar.html',
                            veiculos=veiculos, mecanicos=mecanicos, 
                            agendamentos=agendamentos, servicos=servicos, pecas=pecas)

    @app.route('/ordens/editar/<int:id>', methods=['GET', 'POST'])
    def ordens_editar(id):
        os_obj = OrdemDeServico.query.get_or_404(id)

        servicos = Servico.query.order_by(Servico.nome_servico).all()
        pecas = Peca.query.order_by(Peca.nome_peca).all()
        agendamentos = Agendamento.query.order_by(Agendamento.data_agendamento).all()
        veiculos = Veiculo.query.order_by(Veiculo.placa).all()
        mecanicos = Mecanico.query.order_by(Mecanico.nome).all()

        itens_servico = ItemOrdemServico.query.filter_by(id_ordem_servico=id).all()
        itens_peca = PecaOrdemServico.query.filter_by(id_ordem_servico=id).all()

        def parse_date(val):
            if not val:
                return None
            try:
                # aceita 'YYYY-MM-DD' e 'YYYY-MM-DDTHH:MM' etc.
                return datetime.fromisoformat(val).date()
            except Exception:
                try:
                    return datetime.strptime(val, '%Y-%m-%d').date()
                except Exception:
                    return None

        def parse_time(val):
            if not val:
                return None
            try:
                return datetime.fromisoformat(val).time()
            except Exception:
                for fmt in ('%H:%M:%S', '%H:%M'):
                    try:
                        return datetime.strptime(val, fmt).time()
                    except Exception:
                        continue
            return None

        if request.method == 'POST':
            try:
                os_obj.numero_os = request.form.get('numero_os') or os_obj.numero_os

                data_ab = request.form.get('data_abertura')
                os_obj.data_abertura = parse_date(data_ab)

                data_conc = request.form.get('data_conclusao')
                os_obj.data_conclusao = parse_date(data_conc)

                os_obj.status = request.form.get('status') or os_obj.status
                valor = request.form.get('valor_total')
                os_obj.valor_total = float(valor) if valor not in (None, '') else os_obj.valor_total
                os_obj.observacoes = request.form.get('observacoes') or None

                os_obj.id_agendamento = int(request.form.get('id_agendamento')) if request.form.get('id_agendamento') else None
                os_obj.id_veiculo = int(request.form.get('id_veiculo')) if request.form.get('id_veiculo') else None
                os_obj.id_mecanico = int(request.form.get('id_mecanico')) if request.form.get('id_mecanico') else None

                # se houver campos de hora separados, parse_time pode ser usado
                # Ex: hora_inicio = request.form.get('hora_inicio'); os_obj.hora_inicio = parse_time(hora_inicio)

                db.session.commit()
                flash('Ordem de serviço atualizada.', 'success')
                return redirect(url_for('ordens_listar'))
            except Exception as e:
                db.session.rollback()
                current_app.logger.exception('Erro ao atualizar ordem de serviço')
                flash(f'Erro ao atualizar OS: {e}', 'danger')

        return render_template('ordem_de_servico/editar.html',
                               os=os_obj,
                               servicos=servicos,
                               pecas=pecas,
                               agendamentos=agendamentos,
                               veiculos=veiculos,
                               mecanicos=mecanicos,
                               itens_servico=itens_servico,
                               itens_peca=itens_peca)

    @app.route('/ordens/excluir/<int:id>')
    def ordens_excluir(id):
        try:
            with app.app_context():
                ordem = db.session.query(OrdemDeServico).get(id)
                if ordem:
                    db.session.delete(ordem)
                    db.session.commit()
                    flash("Ordem de serviço removida com sucesso!", "danger")
                else:
                    flash("Ordem de serviço não encontrada!", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao excluir ordem de serviço: {str(e)}", "danger")
        
        return redirect(url_for('ordens_listar'))

    #================================
    # RELATÓRIOS
    #================================

    @app.route('/relatorios')
    def relatorios():
        # placeholder simples — substitua por lógica real quando tiver
        return render_template('relatorios.html')