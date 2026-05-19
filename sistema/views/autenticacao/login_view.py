from flask import render_template, redirect, url_for, request, session, flash
from sistema import app
from datetime import datetime

# ===============================================================================================
# FUNÇÕES AUXILIARES DE DADOS SIMULADOS (DUPLICADAS PARA MANTER A SIMULAÇÃO ISOLADA POR VIEW)
# Em um sistema real, essas funções seriam centralizadas em um módulo de serviços ou models.
# ===============================================================================================

def _get_simulated_rates():
"""Retorna a lista de taxas e juros do sistema."""
return [
    {'id': 1, 'nome': 'Taxa de Juros Nominal (Mensal)', 'valor': '2,50%', 'descricao': 'Taxa padrão para novos empréstimos.', 'ultima_alteracao': 'Ricardo Dantas', 'historico': [{'data': '20/01/2026', 'valor': '2,45%', 'usuario': 'Ricardo'}, {'data': '10/01/2026', 'valor': '2,40%', 'usuario': 'Ricardo'}]},
    {'id': 2, 'nome': 'Taxa de Juros Nominal (Anual)', 'valor': '34,49%', 'descricao': 'Taxa efetiva anual baseada na mensal.', 'ultima_alteracao': 'Sistema', 'historico': []},
    {'id': 3, 'nome': 'Taxa de Juros Máxima', 'valor': '8,00%', 'descricao': 'Limite de segurança para evitar juros abusivos.', 'ultima_alteracao': 'Diretoria', 'historico': []},
    {'id': 4, 'nome': 'Taxa de Inadimplência/Mora (Ao dia)', 'valor': '0,33%', 'descricao': 'Juros aplicados em caso de atraso na parcela.', 'ultima_alteracao': 'Ricardo Dantas', 'historico': []},
    {'id': 5, 'nome': 'Multa por Atraso (%)', 'valor': '2,00%', 'descricao': 'Multa percentual sobre o valor da parcela vencida.', 'ultima_alteracao': 'Ricardo Dantas', 'historico': []},
]

def _get_simulated_payment_history():
"""Retorna um histórico de pagamentos simulado."""
# 1. Definimos a "origem" de cada contrato de forma resumida:
# (Cliente, Tipo, Total Parcelas, Valor, Pagas, Atrasadas, Dia Vencimento)
configuracao = [
    ('Aline Ferreira', 'Consignado', 7, '10.000,00', 1, 1, 12),
    ('Carlos Pereira', 'Empréstimo Rápido', 2, '10.000,00', 0, 1, 10),
    ('Fernanda Lima', 'Pessoal', 10, '600,00', 3, 0, 5),
    ('João Rocha', 'Empréstimo Pessoal', 4, '8.000,00', 3, 0, 10),
    ('José Souza', 'Automotivo', 4, '12.000,00', 3, 0, 20),
    ('Maria Silva', 'Financiamento', 5, '5.000,00', 1, 1, 15),
    ('Roberto Alves', 'Pessoal', 12, '500,00', 3, 0, 15),
]

historico = []
for nome, tipo, total, valor, pagas, atrasadas, dia in configuracao:
    # Criamos as parcelas dinamicamente até a primeira pendente/atrasada
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

        historico.append({
            'id': len(historico) + 1,
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
return historico

def formatar_valor_moeda(valor_float):
"""Formata um número float para o padrão brasileiro (ex: '1.500,00')."""
return f"{valor_float:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def parse_currency(value_str):
"""Converte string de moeda (ex: '1.500,00') em número float."""
return float(str(value_str).replace('.', '').replace(',', '.'))

def _obter_dados_clientes_completos():
"""Simula busca no banco de dados sincronizada com usuario_view.py."""
return [
    {'id': 1, 'nome': 'João Rocha', 'valor_parcela': '8.000,00', 'parcelas_restantes': 1, 'total_parcelas': 4, 'limite_disponivel': '10.000,00', 'emprestimos_ativos': 1, 'taxa': '2,50%', 'detalhes': [{'tipo': 'Pessoal', 'valor': '32.000,00', 'status': 'Pendente', 'vencimento': '10/04/2026'}]},
    {'id': 2, 'nome': 'Maria Silva', 'valor_parcela': '5.000,00', 'parcelas_restantes': 4, 'total_parcelas': 5, 'limite_disponivel': '5.000,00', 'emprestimos_ativos': 1, 'taxa': '2,50%', 'detalhes': [{'tipo': 'Financiamento', 'valor': '25.000,00', 'status': 'Atrasado', 'vencimento': '15/02/2026'}]},
    {'id': 3, 'nome': 'José Souza', 'valor_parcela': '12.000,00', 'parcelas_restantes': 1, 'total_parcelas': 4, 'limite_disponivel': '10.000,00', 'emprestimos_ativos': 1, 'taxa': '2,50%', 'detalhes': [{'tipo': 'Automotivo', 'valor': '48.000,00', 'status': 'Pendente', 'vencimento': '20/04/2026'}]},
    {'id': 4, 'nome': 'Roberto Alves', 'valor_parcela': '500,00', 'parcelas_restantes': 9, 'total_parcelas': 12, 'limite_disponivel': '5.000,00', 'emprestimos_ativos': 1, 'taxa': '2,50%', 'detalhes': [{'tipo': 'Pessoal', 'valor': '6.000,00', 'status': 'Pendente', 'vencimento': '15/04/2026'}]},
    {'id': 5, 'nome': 'Carlos Pereira', 'valor_parcela': '10.000,00', 'parcelas_restantes': 2, 'total_parcelas': 2, 'limite_disponivel': '0,00', 'emprestimos_ativos': 1, 'taxa': '2,50%', 'detalhes': [{'tipo': 'Empréstimo Rápido', 'valor': '20.000,00', 'status': 'Atrasado', 'vencimento': '10/01/2026'}]},
    {'id': 6, 'nome': 'Fernanda Lima', 'valor_parcela': '600,00', 'parcelas_restantes': 7, 'total_parcelas': 10, 'limite_disponivel': '500,00', 'emprestimos_ativos': 1, 'taxa': '2,50%', 'detalhes': [{'tipo': 'Pessoal', 'valor': '6.000,00', 'status': 'Pendente', 'vencimento': '05/04/2026'}]},
    {'id': 7, 'nome': 'Aline Ferreira', 'valor_parcela': '10.000,00', 'parcelas_restantes': 6, 'total_parcelas': 7, 'limite_disponivel': '20.000,00', 'emprestimos_ativos': 1, 'taxa': '2,50%', 'detalhes': [{'valor': '70.000,00', 'vencimento': '12/02/2026'}]},
]

@app.route('/')
def principal():
# Se não estiver logado, manda pro login
if 'usuario_logado' not in session:
    return redirect(url_for('login'))

# Inicialização global das variáveis para evitar NameError/Pylance
hoje_data = datetime(2026, 3, 27).date()
total_pago_real = 0.0
saldo_devedor_real = 0.0
total_emprestimo_principal = 0.0
proxima_parcela_valor_com_encargos = 0.0
proxima_parcela_data = "N/A"
esta_atrasado = False

# Se o perfil for de cliente, preparamos os dados para o painel personalizado
if session.get('perfil') == 'cliente':
    # 1. Obter dados do cliente logado
    id_cliente_logado = session.get('cliente_id')
    dados_clientes = _obter_dados_clientes_completos()
    cliente_atual = next((c for c in dados_clientes if c['id'] == id_cliente_logado), None)

    if not cliente_atual:
        # Caso não encontre o cliente (pouco provável), mostra painel padrão
        return render_template('estrutura/dashboard.html')

    # 2. Configurações Iniciais e Taxas
    total_emprestimo_principal = parse_currency(cliente_atual['detalhes'][0]['valor'])

    taxas_cliente = _get_simulated_rates()
    multa_percentual = parse_currency(next(t['valor'] for t in taxas_cliente if t['id'] == 5).replace('%','')) / 100
    juros_mora_diario_percentual = parse_currency(next(t['valor'] for t in taxas_cliente if t['id'] == 4).replace('%','')) / 100
    juros_max_percentual = parse_currency(next(t['valor'] for t in taxas_cliente if t['id'] == 3).replace('%','')) / 100
    
    # 3. Obter e Processar Histórico para Totais e Gráficos
    historico_cliente_raw = [p for p in _get_simulated_payment_history() if p['cliente'] == cliente_atual['nome']]
    historico_cliente_raw.sort(key=lambda x: datetime.strptime(x['vencimento'], '%d/%m/%Y'))

    found_next = False

    chart_labels = []
    chart_data = []
    chart_status = []

    for item in historico_cliente_raw:
        val_base = parse_currency(item['valor'])
        venc_dt = datetime.strptime(item['vencimento'], '%d/%m/%Y').date()
        
        # Prepara labels do gráfico
        chart_labels.append(venc_dt.strftime('%b/%y'))
        valor_final_parcela = val_base
        
        if item['status'] == 'Pago':
            total_pago_real += val_base
            if 'Pago com atraso' in item.get('obs', ''):
                chart_status.append('pago_atrasado')
            else:
                chart_status.append('pago_em_dia')
        else:
            # Cálculo de encargos para parcelas não pagas (se atrasadas)
            dias_atraso = (hoje_data - venc_dt).days
            if dias_atraso > 0:
                multa = val_base * multa_percentual
                juros = (val_base * juros_mora_diario_percentual) * dias_atraso
                valor_final_parcela += multa + min(juros, val_base * juros_max_percentual)
            
            saldo_devedor_real += valor_final_parcela
            
            # Identifica a próxima parcela a ser exibida nos cards
            if not found_next:
                proxima_parcela_valor_com_encargos = valor_final_parcela
                proxima_parcela_data = item['vencimento']
                esta_atrasado = (item['status'] == 'Atrasado' or dias_atraso > 0)
                found_next = True
            
            # Status para as cores do gráfico
            if item['status'] == 'Atrasado':
                chart_status.append('pendente')
            else:
                if venc_dt.strftime('%m/%Y') == hoje_data.strftime('%m/%Y'):
                    chart_status.append('atual')
                else:
                    chart_status.append('futuro')

        chart_data.append(valor_final_parcela)

    # Consolidação dos dados do gráfico
    historico_chart_data = {
        'labels': chart_labels,
        'datasets': [{'label': 'Valor da Parcela', 'data': chart_data, 'status': chart_status}]
    }

    # 4. Cálculos Finais para os Cards
    percentual_pago = (total_pago_real / total_emprestimo_principal * 100) if total_emprestimo_principal > 0 else 0

    if proxima_parcela_data != "N/A":
        venc_prox = datetime.strptime(proxima_parcela_data, '%d/%m/%Y').date()
        d_restantes = (venc_prox - hoje_data).days
        if d_restantes < 0:
            prazo_texto = f"Venceu em: <b>{proxima_parcela_data}</b> (há {abs(d_restantes)} dias)"
        elif d_restantes == 0:
            prazo_texto = f"Vence em: <b>{proxima_parcela_data}</b> (Hoje)"
        else:
            prazo_texto = f"Vence em: <b>{proxima_parcela_data}</b> (faltam {d_restantes} dias)"
    else:
        prazo_texto = "Empréstimo Quitado"

    dados_dashboard = {
        'data_atual': hoje_data.strftime('%d/%m/%Y'),
        'saldo_devedor': formatar_valor_moeda(saldo_devedor_real),
        'limite_disponivel': cliente_atual.get('limite_disponivel', '0,00'),
        'emprestimos_ativos': cliente_atual.get('emprestimos_ativos', 0),
        'prazo_pagamento': prazo_texto,
        'total_emprestimo': formatar_valor_moeda(total_emprestimo_principal), # Initial principal
        'total_pago': formatar_valor_moeda(total_pago_real), # Real paid amount (base)
        'percentual_pago': int(percentual_pago),
        'proxima_parcela_valor': formatar_valor_moeda(proxima_parcela_valor_com_encargos),
        'proxima_parcela_data': proxima_parcela_data,
        'grafico_progresso': {
            'pago': total_pago_real,
            'restante': saldo_devedor_real
        },
        'historico_chart': historico_chart_data,
        'esta_atrasado': esta_atrasado
    }

    return render_template('estrutura/dashboardclientes.html', dados_dashboard=dados_dashboard)

# --- DADOS E CÁLCULOS PARA O DASHBOARD DO GERENTE ---
# 1. Obter dados dos clientes completos (incluindo os que estão em dia/atrasados)
clientes_completos_para_gerente = _obter_dados_clientes_completos()
taxas_gerente = _get_simulated_rates() # Necessário para calcular juros/multa se for o caso

multa_percentual_gerente = parse_currency(next(t['valor'] for t in taxas_gerente if t['id'] == 5).replace('%','')) / 100
juros_mora_diario_percentual_gerente = parse_currency(next(t['valor'] for t in taxas_gerente if t['id'] == 4).replace('%','')) / 100
juros_max_percentual_gerente = parse_currency(next(t['valor'] for t in taxas_gerente if t['id'] == 3).replace('%','')) / 100

dados_clientes_gerente_processados = []
total_emprestado_geral = 0.0
total_recebido_geral = 0.0
qtd_atrasados_geral = 0
valor_em_dia_geral = 0.0
valor_atrasado_geral = 0.0

# Usar o histórico de pagamentos simulado para calcular o 'recebido' de forma mais realista
historico_completo = _get_simulated_payment_history()

for cliente in clientes_completos_para_gerente:
    total_emprestado_cliente = parse_currency(cliente['detalhes'][0]['valor'])
    valor_parcela_original = parse_currency(cliente['valor_parcela'])
    
    # Determinar status e dias de atraso
    data_vencimento_str = cliente['detalhes'][0]['vencimento']
    data_vencimento = datetime.strptime(data_vencimento_str, '%d/%m/%Y').date()

    # Sincronização Cronológica para o Gerente
    dias_atraso = 0
    if cliente['detalhes'][0]['status'] != 'Pago' and data_vencimento < hoje_data:
        dias_atraso = (hoje_data - data_vencimento).days

    cliente_status_gerente = 'Em Dia'
    if dias_atraso > 0:
        cliente_status_gerente = 'Atrasado'
        qtd_atrasados_geral += 1
    else:
        valor_em_dia_geral += total_emprestado_cliente # Considera o valor total emprestado para em dia

    # Calcular 'recebido' com base nas parcelas pagas do histórico
    paid_parcels_count = sum(1 for p in historico_completo if p['cliente'] == cliente['nome'] and p['status'] == 'Pago')
    valor_recebido_cliente = paid_parcels_count * valor_parcela_original
    
    # Cálculo de Saldo Devedor (Exposição Real)
    saldo_devedor_cliente = total_emprestado_cliente - valor_recebido_cliente
    
    total_emprestado_geral += total_emprestado_cliente
    total_recebido_geral += valor_recebido_cliente

    info_cliente = {
        'nome': cliente['nome'],
        'emprestado': total_emprestado_cliente,
        'recebido': valor_recebido_cliente,
        'status': cliente_status_gerente,
        'dias_atraso': dias_atraso,
        'valor_vencido': cliente['valor_parcela'],
        'saldo_restante': saldo_devedor_cliente
    }
    dados_clientes_gerente_processados.append(info_cliente)
    
    # Segrega o Capital em Risco (Apenas o que falta receber de clientes atrasados)
    if cliente_status_gerente == 'Atrasado':
        valor_atrasado_geral += saldo_devedor_cliente

comparativo_chart_data = {
    'labels': [c['nome'] for c in dados_clientes_gerente_processados],
    'datasets': [
        {
            'label': 'Valor Emprestado',
            'data': [c['emprestado'] for c in dados_clientes_gerente_processados]
        },
        {
            'label': 'Valor Recebido',
            'data': [c['recebido'] for c in dados_clientes_gerente_processados]
        }
    ]
}

# 3. Gerar dados para os cards de resumo (usando os totais calculados)
# Cálculo dinâmico de recebimentos em Março/2026 baseado no histórico
valor_recebido_março = 0.0
for p in historico_completo:
    if p['status'] == 'Pago' and (p.get('data_pagamento') and '/03/2026' in p['data_pagamento']):
        valor_recebido_março += parse_currency(p['valor'])

taxa_atraso = int((qtd_atrasados_geral / len(clientes_completos_para_gerente)) * 100) if clientes_completos_para_gerente else 0

# Cálculos de KPI: Risco sobre a carteira e Índice de Recuperação (Reinvestimento)
percentual_risco = round((valor_atrasado_geral / total_emprestado_geral * 100)) if total_emprestado_geral > 0 else 0
indice_reinvestimento = int((total_recebido_geral / total_emprestado_geral * 100)) if total_emprestado_geral > 0 else 0

resumo_gerente = {
    'total_emprestado': formatar_valor_moeda(total_emprestado_geral),
    'recebimentos_mes': formatar_valor_moeda(valor_recebido_março), # Valor dinâmico do mês atual
    'disponibilidade_caixa': 'R$ 55.000,00', # Esse mantivemos fixo conforme pedido
    'taxa_atraso': f"{taxa_atraso}%", # Usando a taxa calculada
    'capital_em_risco': formatar_valor_moeda(valor_atrasado_geral),
    'percentual_risco': percentual_risco,
    'indice_reinvestimento': indice_reinvestimento
}

# 4. (NOVO) Gerar dados para os outros gráficos do gerente

# 4.1. Gráfico de Situação de Pagamentos (Doughnut)
valor_em_dia = sum(c['emprestado'] for c in dados_clientes_gerente_processados if c['status'] == 'Em Dia')
valor_atrasado = sum(c['emprestado'] for c in dados_clientes_gerente_processados if c['status'] == 'Atrasado')
valor_quitado_simulado = 30000 # Valor simulado para representar empréstimos já finalizados (mantido fixo)
situacao_chart_data = {
    'labels': ['Em Dia', 'Em Atraso', 'Liquidados'],
    'datasets': [{
        'data': [valor_em_dia, valor_atrasado, valor_quitado_simulado],
    }]
}

# 4.2. Gráfico de Previsão de Entradas (Line)
previsao_chart_data = {
    'labels': ["Jan", "Fev", "Mar", "Abr"],
    'datasets': [{
        'label': "Previsão de Entradas",
        'data': [32000, 35000, 21100, 34000]
    }]
}

# 4.3. Gráfico de Lucro Bruto vs Líquido (Bar)
lucro_chart_data = {
    'labels': ["Jan", "Fev", "Mar"],
    'datasets': [{
        'label': "Lucro Bruto",
        'data': [8500, 9200, 8800],
    }, {
        'label': "Lucro Líquido",
        'data': [6000, 6800, 6200],
    }]
}

# Filtra apenas os clientes que estão com status 'Atrasado' para a tabela de Pendências e ordena por nome
pendencias_criticas = sorted([c for c in dados_clientes_gerente_processados if c['status'] == 'Atrasado'], key=lambda x: x['nome'])

# Se for gerente, apenas renderiza o painel padrão
return render_template('estrutura/dashboard.html', dados_dashboard={
    'data_atual': hoje_data.strftime('%d/%m/%Y'),
    'comparativo_chart': comparativo_chart_data,
    'resumo': resumo_gerente,
    'situacao_chart': situacao_chart_data,
    'previsao_chart': previsao_chart_data,
    'lucro_chart': lucro_chart_data,
    'pendencias_criticas': pendencias_criticas
})

@app.route('/login', methods=['GET', 'POST'])
def login():
if request.method == 'POST':
    email = request.form.get('email')
    senha = request.form.get('senha')

    # Simulação de Autenticação (Hardcoded para teste)
    
    # 1. Login do Gerente (Ricardo)
    if email == 'ricardodantasgerente@hotmail.com' and senha == '123456':
        session['usuario_logado'] = 'Ricardo Dantas'
        session['perfil'] = 'gerente'
        session['email'] = 'ricardodantasgerente@hotmail.com'
        session['foto'] = 'profile2.jpg' # Foto do Ricardo
        session['telefone'] = '(11) 99999-9999'
        session['profissao'] = 'Gerente'
        session['estado'] = 'São Paulo'
        session['cidade'] = 'São Paulo'
        return redirect(url_for('principal'))
    
    # 2. Login de Clientes (Simulação via Dicionário)
    clientes_permitidos = {
        # Para cada cliente, definimos o id, nome e a foto correspondente
        'joaorocha@hotmail.com': {'id': 1, 'nome': 'João Rocha', 'foto': 'JoaoRocha.jpg', 'telefone': '(11) 91234-5678', 'profissao': 'Administrativo', 'estado': 'Bahia', 'cidade': 'Salvador'},
        'mariasilva@gmail.com': {'id': 2, 'nome': 'Maria Silva', 'foto': 'portrait-senior-woman-MariaSilva.jpg', 'telefone': '(21) 99876-5432', 'profissao': 'Financeiro', 'estado': 'Minas Gerais', 'cidade': 'Belo Horizonte'},
        'josesouza@gmail.com': {'id': 3, 'nome': 'José Souza', 'foto': 'chadengle-JoseSouza.jpg', 'telefone': '(31) 98765-4321', 'profissao': 'Investidor', 'estado': 'Rio Grande do Sul', 'cidade': 'Porto Alegre'},
        'robertoalves@hotmail.com': {'id': 4, 'nome': 'Roberto Alves', 'foto': 'man-RobertoAlves.jpg', 'telefone': '(41) 91122-3344', 'profissao': 'Desenvolvedor', 'estado': 'Amazonas', 'cidade': 'Manaus'},
        'carlospereira@hotmail.com': {'id': 5, 'nome': 'Carlos Pereira', 'foto': 'man-CarlosPereira.jpg', 'telefone': '(51) 95566-7788', 'profissao': 'Gerente', 'estado': 'Rio de Janeiro', 'cidade': 'Rio de Janeiro'},
        'fernandalima@gmail.com': {'id': 6, 'nome': 'Fernanda Lima', 'foto': 'woman-FernandaLima.jpg', 'telefone': '(61) 94433-2211', 'profissao': 'Administrativo', 'estado': 'Tocantins', 'cidade': 'Palmas'},
        'alineferreira@hotmail.com': {'id': 7, 'nome': 'Aline Ferreira', 'foto': 'portrait-woman-AlineFerreira.jpg', 'telefone': '(71) 97788-9900', 'profissao': 'Desenvolvedor', 'estado': 'São Paulo', 'cidade': 'São Paulo'}
    }

    if email in clientes_permitidos and senha == '123456':
        cliente = clientes_permitidos[email]
        session['usuario_logado'] = cliente['nome']
        session['perfil'] = 'cliente'
        session['cliente_id'] = cliente['id']
        session['email'] = email
        session['foto'] = cliente['foto']
        session['telefone'] = cliente['telefone']
        session['profissao'] = cliente['profissao']
        session['estado'] = cliente['estado']
        session['cidade'] = cliente['cidade']
        return redirect(url_for('principal'))

    else:
        flash('Email ou senha incorretos.', 'danger')
        return redirect(url_for('login'))

return render_template('autenticacao/login.html')
