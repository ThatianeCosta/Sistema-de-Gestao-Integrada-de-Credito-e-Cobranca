from sistema import app, db
from flask import render_template, request, redirect, url_for, flash, session
from datetime import datetime
from sistema.models.autenticacao.role_model import RoleModel
from sistema.models.autenticacao.usuario_model import UsuarioModel

# ===============================================================================================
# FUNÇÕES AUXILIARES DE DADOS SIMULADOS
# Em um sistema real, essas funções fariam consultas ao banco de dados.
# Manter os dados aqui centraliza a simulação e limpa as funções de rota.
# ===============================================================================================

def parse_currency(value_str):
    """Converte string de moeda (ex: '1.500,00') em número float."""
    return float(str(value_str).replace('.', '').replace(',', '.'))

def formatar_valor_moeda(valor_float):
    """Formata um número float para o padrão brasileiro (ex: '1.500,00')."""
    return f"{valor_float:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def _get_simulated_clients():
    """Retorna uma lista de clientes simulados."""
    return [
        {'id': 7, 'nome': 'Aline Ferreira', 'email': 'alineferreira@hotmail.com', 'emprestimos_ativos': 1, 'status': 'Atrasado', 'rating': 'A', 'valor_parcela': '10.000,00', 'total_parcelas': 7, 'parcelas_restantes': 6, 'limite_disponivel': '20.000,00', 'taxa': '2,50%', 'detalhes': [{'tipo': 'Consignado', 'valor': '70.000,00', 'status': 'Atrasado', 'vencimento': '12/02/2026'}]},
        {'id': 5, 'nome': 'Carlos Pereira', 'email': 'carlospereira@hotmail.com', 'emprestimos_ativos': 1, 'status': 'Atrasado', 'rating': 'E', 'valor_parcela': '10.000,00', 'total_parcelas': 2, 'parcelas_restantes': 2, 'limite_disponivel': '0,00', 'taxa': '2,50%', 'detalhes': [{'tipo': 'Empréstimo Rápido', 'valor': '20.000,00', 'status': 'Atrasado', 'vencimento': '10/01/2026'}]},
        {'id': 6, 'nome': 'Fernanda Lima', 'email': 'fernandalima@gmail.com', 'emprestimos_ativos': 1, 'status': 'Em Dia', 'rating': 'C', 'valor_parcela': '600,00', 'total_parcelas': 10, 'parcelas_restantes': 7, 'limite_disponivel': '500,00', 'taxa': '2,50%', 'detalhes': [{'tipo': 'Pessoal', 'valor': '6.000,00', 'status': 'Pendente', 'vencimento': '05/04/2026'}]},
        {'id': 1, 'nome': 'João Rocha', 'email': 'joaorocha@hotmail.com', 'emprestimos_ativos': 1, 'status': 'Em Dia', 'rating': 'A', 'valor_parcela': '8.000,00', 'total_parcelas': 4, 'parcelas_restantes': 1, 'limite_disponivel': '10.000,00', 'taxa': '2,50%', 'detalhes': [{'tipo': 'Pessoal', 'valor': '32.000,00', 'status': 'Pendente', 'vencimento': '10/04/2026'}]},
        {'id': 3, 'nome': 'José Souza', 'email': 'josesouza@gmail.com', 'emprestimos_ativos': 1, 'status': 'Em Dia', 'rating': 'B', 'valor_parcela': '12.000,00', 'total_parcelas': 4, 'parcelas_restantes': 1, 'limite_disponivel': '10.000,00', 'taxa': '2,50%', 'detalhes': [{'tipo': 'Automotivo', 'valor': '48.000,00', 'status': 'Pendente', 'vencimento': '20/04/2026'}]},
        {'id': 2, 'nome': 'Maria Silva', 'email': 'mariasilva@gmail.com', 'emprestimos_ativos': 1, 'status': 'Atrasado', 'rating': 'B', 'valor_parcela': '5.000,00', 'total_parcelas': 5, 'parcelas_restantes': 4, 'limite_disponivel': '5.000,00', 'taxa': '2,50%', 'detalhes': [{'tipo': 'Financiamento', 'valor': '25.000,00', 'status': 'Atrasado', 'vencimento': '15/02/2026'}]},
        {'id': 4, 'nome': 'Roberto Alves', 'email': 'robertoalves@hotmail.com', 'emprestimos_ativos': 1, 'status': 'Em Dia', 'rating': 'D', 'valor_parcela': '500,00', 'total_parcelas': 12, 'parcelas_restantes': 9, 'limite_disponivel': '5.000,00', 'taxa': '2,50%', 'detalhes': [{'tipo': 'Pessoal', 'valor': '6.000,00', 'status': 'Pendente', 'vencimento': '15/04/2026'}]},
    ]

def _get_simulated_payment_history():
    """Retorna o histórico de parcelas. Nota: Cada cliente possui múltiplas entradas representando as parcelas mensais."""
    # Configuração mestre: (Cliente, Tipo, Total, Valor, Pagas, Atrasadas, Dia)
    config = [
        ('Aline Ferreira', 'Consignado', 7, '10.000,00', 1, 1, 12),
        ('Carlos Pereira', 'Empréstimo Rápido', 2, '10.000,00', 0, 1, 10),
        ('Fernanda Lima', 'Pessoal', 10, '600,00', 3, 0, 5),
        ('João Rocha', 'Empréstimo Pessoal', 4, '8.000,00', 3, 0, 10),
        ('José Souza', 'Automotivo', 4, '12.000,00', 3, 0, 20),
        ('Maria Silva', 'Financiamento', 5, '5.000,00', 1, 1, 15),
        ('Roberto Alves', 'Pessoal', 12, '500,00', 3, 0, 15),
    ]

    resultado = []
    for nome, tipo, total, valor, pagas, atrasadas, dia in config:
        for n in range(1, total + 1):
            status = "Pendente"
            data_pago = None
            obs = "Aguardando vencimento"

            if n <= pagas:
                status = "Pago"
                data_pago = f"{dia:02d}/{n:02d}/2026"
                obs = "Pago em dia"
            elif n <= pagas + atrasadas:
                status = "Atrasado"
                obs = "Aguardando pagamento"

            resultado.append({
                'id': len(resultado) + 1,
                'cliente': nome,
                'descricao': f"{tipo} - Parc. {n}/{total}",
                'num_parcela': n,
                'total_parcelas': total,
                'vencimento': f"{dia:02d}/{n:02d}/2026",
                'data_pagamento': data_pago,
                'valor': valor,
                'status': status,
                'obs': obs
            })
    return resultado

def _get_simulated_cash_flow_base():
    """Retorna a base para o fluxo de caixa simulado (Perspectiva da Empresa: Entradas = Recebimentos, Saídas = Empréstimos Concedidos)."""
    return [
        {'cliente': 'Aline Ferreira', 'entradas': '10.000,00', 'saidas': '70.000,00'},
        {'cliente': 'Carlos Pereira', 'entradas': '0,00', 'saidas': '20.000,00'},
        {'cliente': 'Fernanda Lima', 'entradas': '1.800,00', 'saidas': '6.000,00'},
        {'cliente': 'João Rocha', 'entradas': '24.000,00', 'saidas': '32.000,00'},
        {'cliente': 'José Souza', 'entradas': '36.000,00', 'saidas': '48.000,00'},
        {'cliente': 'Maria Silva', 'entradas': '5.000,00', 'saidas': '25.000,00'},
        {'cliente': 'Roberto Alves', 'entradas': '1.500,00', 'saidas': '6.000,00'},
    ]

def _get_simulated_reports():
    """Retorna uma lista de relatórios de crédito simulados."""
    return [
        {'id': 7, 'cliente': 'Aline Ferreira', 'score': 380, 'risco': 'Alto', 'limite_sugerido': '5.000,00', 'ultima_analise': '12/01/2026', 'obs': 'Risco elevado detectado devido ao atraso na parcela atual. Suspensão de novos créditos recomendada.'},
        {'id': 5, 'cliente': 'Carlos Pereira', 'score': 320, 'risco': 'Alto', 'limite_sugerido': '0,00', 'ultima_analise': '10/01/2026', 'obs': 'Inadimplência recorrente. Não recomendado para novos créditos no momento.'},
        {'id': 6, 'cliente': 'Fernanda Lima', 'score': 620, 'risco': 'Médio', 'limite_sugerido': '500,00', 'ultima_analise': '05/01/2026', 'obs': 'Perfil estável, mas com limite de crédito reduzido preventivamente pelo sistema.'},
        {'id': 1, 'cliente': 'João Rocha', 'score': 910, 'risco': 'Baixo', 'limite_sugerido': '10.000,00', 'ultima_analise': '10/01/2026', 'obs': 'Cliente premium. Score elevado e pagamentos rigorosamente em dia.'},
        {'id': 3, 'cliente': 'José Souza', 'score': 780, 'risco': 'Baixo', 'limite_sugerido': '10.000,00', 'ultima_analise': '20/01/2026', 'obs': 'Bom perfil investidor. Risco controlado e garantias sólidas.'},
        {'id': 2, 'cliente': 'Maria Silva', 'score': 420, 'risco': 'Médio', 'limite_sugerido': '10.000,00', 'ultima_analise': '10/01/2026', 'obs': 'Apresenta atraso na parcela vigente. Monitoramento necessário para evitar inadimplência prolongada.'},
        {'id': 4, 'cliente': 'Roberto Alves', 'score': 550, 'risco': 'Médio', 'limite_sugerido': '10.000,00', 'ultima_analise': '05/02/2026', 'obs': 'Cliente com atrasos recentes. Monitorar.'},
    ]

def _get_simulated_rates():
    """Retorna a lista de taxas e juros do sistema."""
    return [
        {'id': 1, 'nome': 'Taxa de Juros Nominal (Mensal)', 'valor': '2,50%', 'descricao': 'Taxa padrão para novos empréstimos.', 'ultima_alteracao': 'Ricardo Dantas', 'historico': [{'data': '20/01/2026', 'valor': '2,45%', 'usuario': 'Ricardo'}, {'data': '10/01/2026', 'valor': '2,40%', 'usuario': 'Ricardo'}]},
        {'id': 2, 'nome': 'Taxa de Juros Nominal (Anual)', 'valor': '34,49%', 'descricao': 'Taxa efetiva anual baseada na mensal.', 'ultima_alteracao': 'Sistema', 'historico': []},
        {'id': 3, 'nome': 'Taxa de Juros Máxima', 'valor': '8,00%', 'descricao': 'Limite de segurança para evitar juros abusivos.', 'ultima_alteracao': 'Diretoria', 'historico': []},
        {'id': 4, 'nome': 'Taxa de Inadimplência/Mora (Ao dia)', 'valor': '0,33%', 'descricao': 'Juros aplicados em caso de atraso na parcela.', 'ultima_alteracao': 'Ricardo Dantas', 'historico': []},
        {'id': 5, 'nome': 'Multa por Atraso (%)', 'valor': '2,00%', 'descricao': 'Multa percentual sobre o valor da parcela vencida.', 'ultima_alteracao': 'Ricardo Dantas', 'historico': []},
    ]

# ===============================================================================================
# ROTAS DE AUTENTICAÇÃO E NAVEGAÇÃO
# ===============================================================================================

@app.route('/usuarios')
def usuarios_listar():
    usuarios = UsuarioModel.obter_todos_usuarios()
    cargos = RoleModel.obter_roles_asc_cargo()

    # Se for cliente, mostra apenas o próprio usuário (se existir no banco)
    if session.get('perfil') == 'cliente':
        usuario_logado = session.get('usuario_logado')
        usuarios = [u for u in usuarios if f"{u.nome} {u.sobrenome}" == usuario_logado]

    return render_template(
        'autenticacao/usuarios_listar.html',
        usuarios=usuarios,
        cargos=cargos
    )

@app.route('/usuarios/cadastrar', methods=['GET', 'POST'])
def usuarios_cadastrar():
    cargos = RoleModel.obter_roles_asc_cargo()

    if request.method == 'POST':
        nome = request.form.get('campoNome')
        sobrenome = request.form.get('campoSobrenome')
        email = request.form.get('campoEmail')
        telefone = request.form.get('campoTelefone')
        cargo_id = request.form.get('cargoId')
        senha = request.form.get('senha')
        senha_repetir = request.form.get('repetirSenha')

        if not all([nome, sobrenome, email, telefone, cargo_id, senha, senha_repetir]):
            flash('Todos os campos são obrigatórios!', 'danger')
            return redirect(url_for('usuarios_cadastrar'))

        if senha != senha_repetir:
            flash('As senhas não coincidem!', 'danger')
            return redirect(url_for('usuarios_cadastrar'))

        usuario_existente = UsuarioModel.obter_usuario_por_email(email)
        if usuario_existente:
            flash('Este email já está cadastrado!', 'warning')
            return redirect(url_for('usuarios_cadastrar'))

        novo_usuario = UsuarioModel(
            nome=nome,
            sobrenome=sobrenome,
            email=email,
            telefone=telefone,
            senha=senha,
            role_id=cargo_id,
            foto_perfil_id=None,
            ativo=True
        )
        db.session.add(novo_usuario)
        db.session.commit()

        flash('Usuário cadastrado com sucesso!', 'success')
        return redirect(url_for('usuarios_listar'))

    return render_template(
        'autenticacao/usuarios_cadastrar.html',
        cargos = cargos
    )

@app.route('/usuarios/editar/<int:id>', methods=['GET', 'POST'])
def usuarios_editar(id):
    usuario = UsuarioModel.query.get_or_404(id)
    
    if request.method == 'POST':
        usuario.nome = request.form.get('campoNome')
        usuario.sobrenome = request.form.get('campoSobrenome')
        usuario.email = request.form.get('campoEmail')
        usuario.telefone = request.form.get('campoTelefone')
        usuario.role_id = request.form.get('cargoId')
        
        db.session.commit()
        flash('Dados do usuário atualizados com sucesso!', 'success')
        
    return redirect(url_for('usuarios_listar'))

@app.route('/usuarios/excluir/<int:id>')
def usuarios_excluir(id):
    usuario = UsuarioModel.query.get_or_404(id)
    usuario.excluir()
    flash('Usuário excluído com sucesso!', 'success')
    return redirect(url_for('usuarios_listar'))

@app.route('/minha-conta')
def minha_conta():
    # Prepara os dados do usuário logado baseados na sessão
    nome_completo = session.get('usuario_logado', 'Usuário')
    partes_nome = nome_completo.split(' ', 1)
    
    usuario_dados = {
        'nome': partes_nome[0],
        'sobrenome': partes_nome[1] if len(partes_nome) > 1 else '',
        'email': session.get('email', ''),
        'telefone': session.get('telefone', ''),
        'profissao': session.get('profissao', ''),
        'estado': session.get('estado', ''),
        'cidade': session.get('cidade', '')
    }
    return render_template('autenticacao/minha_conta.html', usuario=usuario_dados)

@app.route('/sair')
def sair():
    session.clear() # Limpa a sessão ao sair
    return render_template('autenticacao/sair.html')

@app.route('/clientes')
def clientes_listar():
    # Obtém a lista de clientes da função auxiliar
    clientes_carteira = _get_simulated_clients()

    # --- CÁLCULO DOS TOTAIS PARA OS CARDS ---
    total_clientes = 0
    soma_parcelas_float = 0.0
    soma_parcelas_atrasadas_float = 0.0

    # Apenas o gerente vê os totais da carteira inteira
    if session.get('perfil') == 'gerente':
        total_clientes = len(clientes_carteira)
        for cliente in clientes_carteira:
            valor_parcela = parse_currency(cliente['valor_parcela'])
            soma_parcelas_float += valor_parcela
            
            # Se o cliente estiver atrasado, soma o valor da parcela dele ao total de atrasos
            if cliente['status'] == 'Atrasado':
                soma_parcelas_atrasadas_float += valor_parcela

    soma_parcelas_formatada = formatar_valor_moeda(soma_parcelas_float)
    soma_parcelas_atrasadas_formatada = formatar_valor_moeda(soma_parcelas_atrasadas_float)

    # LÓGICA DE FILTRO POR PERFIL (NOVO)
    # Se o perfil for 'cliente', filtramos a lista para mostrar apenas o ID dele
    if session.get('perfil') == 'cliente':
        id_cliente_logado = session.get('cliente_id')
        clientes_carteira = [c for c in clientes_carteira if c['id'] == id_cliente_logado]

    return render_template('clientes/clientes.html', 
                           clientes=clientes_carteira,
                           total_clientes=total_clientes,
                           soma_parcelas=soma_parcelas_formatada,
                           soma_parcelas_atrasadas=soma_parcelas_atrasadas_formatada)

@app.route('/historico-pagamentos')
def historico_pagamentos():
    # Simulação de dados vindos do banco de dados
    # Obtém a lista de pagamentos da função auxiliar
    lista_periodos = _get_simulated_payment_history()

    # Se for cliente, filtra para mostrar apenas o seu histórico e prepara dados adicionais
    if session.get('perfil') == 'cliente':
        usuario_logado = session.get('usuario_logado')
        movimentacoes_cliente = [p for p in lista_periodos if p['cliente'] == usuario_logado]
        
        # Para o cliente, removemos a coluna 'cliente' dos dados para evitar redundância no HTML
        for p in movimentacoes_cliente:
            p.pop('cliente', None)

        # --- LÓGICA PARA A VISÃO DO CLIENTE ---

        taxas = _get_simulated_rates()
        multa_percentual = parse_currency(next(t['valor'] for t in taxas if t['id'] == 5).replace('%','')) / 100
        juros_mora_diario_percentual = parse_currency(next(t['valor'] for t in taxas if t['id'] == 4).replace('%','')) / 100
        juros_max_percentual = parse_currency(next(t['valor'] for t in taxas if t['id'] == 3).replace('%','')) / 100

        # Para garantir que a simulação de atraso funcione, definimos uma data "hoje" fixa para o ambiente de teste.
        # Alterado para 27/03/2026 conforme solicitado.
        hoje_simulado = datetime(2026, 3, 27).date()
        
        for periodo in movimentacoes_cliente:
            valor_parcela_float = parse_currency(periodo['valor'])
            periodo['valor_fixo_formatado'] = formatar_valor_moeda(valor_parcela_float)
            periodo['acrescimos_formatado'] = "0,00"
            periodo['valor_atualizado_formatado'] = formatar_valor_moeda(valor_parcela_float)
            periodo['detalhes_calculo'] = {} # Inicializa com um dicionário vazio

            data_vencimento = datetime.strptime(periodo['vencimento'], '%d/%m/%Y').date()
            dias_atraso = (hoje_simulado - data_vencimento).days

            if periodo['status'] != 'Pago' and dias_atraso > 0:
                periodo['status'] = 'Atrasado' # Sincroniza o status visual
                multa = valor_parcela_float * multa_percentual
                juros_calculado = (valor_parcela_float * juros_mora_diario_percentual) * dias_atraso
                juros_final = min(juros_calculado, valor_parcela_float * juros_max_percentual)
                
                acrescimos_float = multa + juros_final
                valor_updated_float = valor_parcela_float + acrescimos_float
                periodo['acrescimos_formatado'] = formatar_valor_moeda(acrescimos_float)
                periodo['valor_atualizado_formatado'] = formatar_valor_moeda(valor_updated_float)
                
                # Adiciona os detalhes do cálculo para serem usados no modal
                periodo['detalhes_calculo'] = {
                    'dias_atraso': dias_atraso, 'multa': f"R$ {formatar_valor_moeda(multa)}", 'juros': f"R$ {formatar_valor_moeda(juros_final)}"
                }

        # --- DADOS PARA OS CARDS DE RESUMO ---
        resumo_pagamentos = {}
        clientes_carteira = _get_simulated_clients()
        id_cliente_logado = session.get('cliente_id')
        cliente_atual = next((c for c in clientes_carteira if c['id'] == id_cliente_logado), None) # This is where the client's details are pulled from

        if cliente_atual and movimentacoes_cliente:
            total_emprestimo_str = cliente_atual['detalhes'][0]['valor']
            resumo_pagamentos['total_emprestimo'] = total_emprestimo_str

            total_parcelas = cliente_atual.get('total_parcelas', 0)
            parcelas_pagas = total_parcelas - cliente_atual['parcelas_restantes']
            resumo_pagamentos['parcelas_quitadas'] = f"{parcelas_pagas} de {total_parcelas}"
            
            proximas_parcelas = sorted([p for p in movimentacoes_cliente if p['status'] in ['Pendente', 'Atrasado']], key=lambda x: datetime.strptime(x['vencimento'], '%d/%m/%Y'))
            if proximas_parcelas:
                proxima = proximas_parcelas[0]
                resumo_pagamentos['proximo_vencimento_data'] = proxima['vencimento']
                resumo_pagamentos['proximo_vencimento_valor'] = proxima['valor_atualizado_formatado']
            else:
                resumo_pagamentos['proximo_vencimento_data'] = "N/A"
                resumo_pagamentos['proximo_vencimento_valor'] = "Empréstimo Quitado"
        else:
             resumo_pagamentos = {'total_emprestimo': 'R$ 0,00', 'parcelas_quitadas': '0 de 0', 'proximo_vencimento_data': 'N/A', 'proximo_vencimento_valor': 'N/A'}

        return render_template('financeiro/historicopag.html', periodos=movimentacoes_cliente, resumo=resumo_pagamentos)

    # --- LÓGICA PARA A VISÃO DO GERENTE ---
    hoje_simulado = datetime(2026, 3, 27).date() # Keep this for manager's view of history

    # 1. Primeiro, ordenamos tudo por data para garantir a sequência correta
    lista_periodos.sort(key=lambda x: (x['cliente'], datetime.strptime(x['vencimento'], '%d/%m/%Y')))

    # 2. Criamos um dicionário para guardar apenas a parcela "Mais Importante" de cada contrato
    resumo_gerente = {}

    for item in lista_periodos:
        # Criamos uma chave única para o contrato (Nome do Cliente + Tipo de Empréstimo)
        # Ex: ("Aline Ferreira", "Consignado")
        tipo_emprestimo = item['descricao'].split(' - ')[0]
        chave_contrato = (item['cliente'], tipo_emprestimo)

        # Se ainda não adicionamos esse contrato OU se a parcela que encontramos agora 
        # é a que o gerente precisa ver (a primeira que não está paga)
        if chave_contrato not in resumo_gerente:
            resumo_gerente[chave_contrato] = item
        else:
            parcela_salva = resumo_gerente[chave_contrato]
            # Se a que está salva já foi PAGA, mas a nova que encontramos está PENDENTE ou ATRASADA, 
            # nós trocamos. O objetivo é sempre mostrar a "pendência atual".
            if parcela_salva['status'] == 'Pago' and item['status'] != 'Pago':
                resumo_gerente[chave_contrato] = item

    # Transformamos o resumo de volta em uma lista para o HTML
    lista_filtrada = list(resumo_gerente.values())

    # Obter taxas para o gerente cobrar o valor correto (multa + juros)
    taxas = _get_simulated_rates()
    multa_pct = parse_currency(next(t['valor'] for t in taxas if t['id'] == 5).replace('%','')) / 100
    juros_diario_pct = parse_currency(next(t['valor'] for t in taxas if t['id'] == 4).replace('%','')) / 100
    juros_max_pct = parse_currency(next(t['valor'] for t in taxas if t['id'] == 3).replace('%','')) / 100

    for item in lista_filtrada:
        item['dias_atraso'] = 0
        valor_base = parse_currency(item['valor'])
        # Inicializa o valor atualizado com o valor base (será alterado se houver atraso)
        item['valor_atualizado'] = item['valor']
        
        data_vencimento = datetime.strptime(item['vencimento'], '%d/%m/%Y').date()
        dias = (hoje_simulado - data_vencimento).days

        if item['status'] != 'Pago' and dias > 0:
            item['status'] = 'Atrasado' # Garante que o gerente veja como atrasado se a data passou
            item['dias_atraso'] = dias
            multa = valor_base * multa_pct
            juros = (valor_base * juros_diario_pct) * dias
            total_encargos = multa + min(juros, valor_base * juros_max_pct)
            item['valor_atualizado'] = formatar_valor_moeda(valor_base + total_encargos)

    return render_template('financeiro/historicopag.html', periodos=lista_filtrada)

@app.route('/periodos')
def periodos_redirect():
    return redirect(url_for('historico_pagamentos'))

@app.route('/fluxo-caixa')
def fluxo_caixa():
    # Simulação de dados de fluxo de caixa
    # Obtém dados das funções auxiliares para manter a consistência
    clientes_carteira = _get_simulated_clients()
    lista_periodos = _get_simulated_payment_history()
    fluxo = _get_simulated_cash_flow_base()
    
    taxa_padrao = 0.025 # 2,50%

    # Cálculo automático de Saldo, Status e Lucro (Jeito mais simples)
    for item in fluxo:
        # Sincronização automática das entradas baseada no histórico real de parcelas pagas
        pagas = sum(1 for p in lista_periodos if p['cliente'] == item['cliente'] and p['status'] == 'Pago')
        val_parc = 0.0
        for c in clientes_carteira:
            if c['nome'] == item['cliente']:
                val_parc = parse_currency(c['valor_parcela'])
                break
        item['entradas'] = formatar_valor_moeda(pagas * val_parc)

        v_entrada = parse_currency(item['entradas'])
        v_saida = parse_currency(item['saidas'])
        v_saldo = v_entrada - v_saida

        # Formatar saldo (Exibimos o valor absoluto para representar a dívida restante)
        item['saldo'] = formatar_valor_moeda(abs(v_saldo))

        # Definir Status
        if v_saldo >= 0:
            item['status'] = 'Liquidado'
        else:
            item['status'] = 'Em Aberto'

        # 2. Calcular Lucro Realizado (Jeito Iniciante)
        valor_emprestado = 0.0
        parcelas_pagas = 0

        # Procurar valor do empréstimo na lista de clientes
        for cliente in clientes_carteira:
            if cliente['nome'] == item['cliente']:
                if len(cliente['detalhes']) > 0:
                    valor_emprestado = parse_currency(cliente['detalhes'][0]['valor'])
                break 
        taxa_juros = taxa_padrao

        # Calcular parcelas pagas baseado na carteira de clientes para evitar redundância na história
        parcelas_pagas = 0
        for c in clientes_carteira:
            if c['nome'] == item['cliente']:
                parcelas_pagas = c['total_parcelas'] - c['parcelas_restantes']
                break

        # Fórmula: Lucro = Valor Emprestado * Taxa * Parcelas Pagas
        lucro = valor_emprestado * taxa_juros * parcelas_pagas
        
        item['lucro_acumulado'] = formatar_valor_moeda(lucro)

    # Se for cliente, filtra para mostrar apenas o seu fluxo
    if session.get('perfil') == 'cliente':
        usuario_logado = session.get('usuario_logado')
        fluxo = [f for f in fluxo if f['cliente'] == usuario_logado]

    # --- CÁLCULO DINÂMICO DO RESUMO ---
    # Calcula os totais com base na lista 'fluxo' (que já está filtrada para cliente ou completa para gerente)
    total_entradas_f = 0.0
    total_saidas_f = 0.0

    for item in fluxo:
        # Converte texto (ex: "1.500,00") para número (1500.00) antes de somar
        valor_entrada = parse_currency(item['entradas'])
        total_entradas_f += valor_entrada

        valor_saida = parse_currency(item['saidas'])
        total_saidas_f += valor_saida

    saldo_liquido_f = total_entradas_f - total_saidas_f

    # Cálculo de Inadimplência Atual (Nova solicitação)
    # Inadimplência = Total Atrasado / (Total Pago + Total Atrasado) ou simplificado baseada na carteira
    # Aqui usamos uma simulação baseada nos clientes em atraso vs total emprestado
    total_emprestado_carteira = 0.0
    total_atrasado_carteira = 0.0 # This should be the sum of 'emprestado' for clients with status 'Atrasado'
    for cli in clientes_carteira:
        if len(cli['detalhes']) > 0:
             val = parse_currency(cli['detalhes'][0]['valor'])
             total_emprestado_carteira += val
             if cli['status'] == 'Atrasado':
                 total_atrasado_carteira += val
    taxa_inadimplencia = (total_atrasado_carteira / total_emprestado_carteira * 100) if total_emprestado_carteira > 0 else 0

    resumo = {
        'total_pago': formatar_valor_moeda(total_entradas_f),
        'valor_contratado': formatar_valor_moeda(total_saidas_f),
        'saldo_devedor': formatar_valor_moeda(abs(saldo_liquido_f)),
        'inadimplencia': f"{taxa_inadimplencia:.1f}%"
    }

    # VERIFICAÇÃO PARA CLIENTE (NOVO):
    # Se for cliente, enviamos para a tela de 'Extrato Detalhado' em vez do fluxo de caixa genérico
    if session.get('perfil') == 'cliente':
        usuario_logado = session.get('usuario_logado')
        # Filtra as movimentações (histórico) apenas deste cliente para exibir na tabela
        movimentacoes = [m for m in lista_periodos if m['cliente'] == usuario_logado]

        # --- SINCRONIZAÇÃO DE VALORES COM JUROS (NOVO) ---
        # Atualiza os valores do extrato para incluir encargos, evitando informações desencontradas
        taxas = _get_simulated_rates()
        multa_pct = parse_currency(next(t['valor'] for t in taxas if t['id'] == 5).replace('%','')) / 100
        juros_diario_pct = parse_currency(next(t['valor'] for t in taxas if t['id'] == 4).replace('%','')) / 100
        juros_max_pct = parse_currency(next(t['valor'] for t in taxas if t['id'] == 3).replace('%','')) / 100
        hoje_simulado = datetime(2026, 3, 27).date()

        for mov in movimentacoes:
            val_float = parse_currency(mov['valor'])
            mov['valor_atualizado_formatado'] = formatar_valor_moeda(val_float)

            venc_dt = datetime.strptime(mov['vencimento'], '%d/%m/%Y').date()
            dias = (hoje_simulado - venc_dt).days

            if mov['status'] != 'Pago' and dias > 0:
                mov['status'] = 'Atrasado' # Sincroniza o badge de status no extrato detalhado
                multa = val_float * multa_pct
                juros = (val_float * juros_diario_pct) * dias
                encargos = multa + min(juros, val_float * juros_max_pct)
                mov['valor_atualizado_formatado'] = formatar_valor_moeda(val_float + encargos)

        return render_template('financeiro/extrato_cliente.html', fluxo=fluxo, resumo=resumo, movimentacoes=movimentacoes)

    return render_template('financeiro/fluxo_caixa.html', fluxo=fluxo, resumo=resumo)

@app.route('/relatorios')
def relatorios():
    # Simulação de dados de relatórios financeiros/crédito
    relatorios_clientes = _get_simulated_reports()

    # Lógica de Pesquisa: Filtra a lista se houver um termo 'q' na URL, na barra pesquisa ao digitar o nome do cliente irá abrir o relatório dele
    termo_pesquisa = request.args.get('q')
    if termo_pesquisa:
        relatorios_clientes = [r for r in relatorios_clientes if termo_pesquisa.lower() in r['cliente'].lower()]

    # Se for cliente, filtra para mostrar apenas o seu relatório
    if session.get('perfil') == 'cliente':
        usuario_logado = session.get('usuario_logado')
        relatorios_clientes = [r for r in relatorios_clientes if r['cliente'] == usuario_logado]

    # --- CÁLCULOS PARA OS CARDS DE RESUMO ---
    total_analisados = len(relatorios_clientes)
    clientes_alto_risco = 0
    soma_limite = 0.0
    soma_score = 0

    for r in relatorios_clientes:
        if r['risco'] == 'Alto':
            clientes_alto_risco += 1
        
        # Limpa a formatação (ex: "50.000,00" -> 50000.0) para somar
        val_limite = parse_currency(r['limite_sugerido'])
        soma_limite += val_limite
        
        soma_score += r['score']

    # Calcula média (evita divisão por zero)
    media_score = round(soma_score / total_analisados) if total_analisados > 0 else 0
    
    total_limite_formatado = formatar_valor_moeda(soma_limite)

    return render_template('financeiro/relatorios.html', 
                           relatorios=relatorios_clientes,
                           total_analisados=total_analisados,
                           clientes_alto_risco=clientes_alto_risco,
                           total_limite=total_limite_formatado,
                           media_score=media_score)

@app.route('/taxas')
def taxas():
    # Simulação de Taxas e Juros do sistema
    lista_variaveis = _get_simulated_rates()
    return render_template('financeiro/taxas.html', taxas=lista_variaveis)

@app.route('/variaveis')
def variaveis_redirect():
    return redirect(url_for('taxas'))
