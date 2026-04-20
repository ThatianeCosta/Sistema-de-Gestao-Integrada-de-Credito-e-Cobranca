from flask import render_template, redirect, url_for, request, session, flash
from sistema import app
from datetime import datetime

def formatar_valor_moeda(valor_float):
    """Formata um número float para o padrão brasileiro (ex: '1.500,00')."""
    return f"{valor_float:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def parse_currency(value_str):
    """Converte string de moeda (ex: '1.500,00') em número float."""
    return float(str(value_str).replace('.', '').replace(',', '.'))

def _obter_dados_clientes_completos():
    """Simula busca no banco de dados sincronizada com usuario_view.py."""
    return [
        {'id': 1, 'nome': 'João Rocha', 'valor_parcela': '8.000,00', 'parcelas_restantes': 2, 'total_parcelas': 4, 'limite_disponivel': '10.000,00', 'emprestimos_ativos': 1, 'detalhes': [{'valor': '32.000,00', 'vencimento': '10/02/2026'}]},
        {'id': 2, 'nome': 'Maria Silva', 'valor_parcela': '5.000,00', 'parcelas_restantes': 4, 'total_parcelas': 5, 'limite_disponivel': '5.000,00', 'emprestimos_ativos': 1, 'detalhes': [{'valor': '25.000,00', 'vencimento': '15/02/2026'}]},
        {'id': 3, 'nome': 'José Souza', 'valor_parcela': '12.000,00', 'parcelas_restantes': 3, 'total_parcelas': 4, 'limite_disponivel': '10.000,00', 'emprestimos_ativos': 1, 'detalhes': [{'valor': '48.000,00', 'vencimento': '20/02/2026'}]},
        {'id': 4, 'nome': 'Roberto Alves', 'valor_parcela': '500,00', 'parcelas_restantes': 11, 'total_parcelas': 12, 'limite_disponivel': '5.000,00', 'emprestimos_ativos': 1, 'detalhes': [{'valor': '6.000,00', 'vencimento': '15/02/2026'}]},
        {'id': 5, 'nome': 'Carlos Pereira', 'valor_parcela': '10.000,00', 'parcelas_restantes': 2, 'total_parcelas': 2, 'limite_disponivel': '0,00', 'emprestimos_ativos': 1, 'detalhes': [{'valor': '20.000,00', 'vencimento': '10/12/2025'}]},
        {'id': 6, 'nome': 'Fernanda Lima', 'valor_parcela': '600,00', 'parcelas_restantes': 8, 'total_parcelas': 10, 'limite_disponivel': '500,00', 'emprestimos_ativos': 1, 'detalhes': [{'valor': '6.000,00', 'vencimento': '05/02/2026'}]},
        {'id': 7, 'nome': 'Aline Ferreira', 'valor_parcela': '10.000,00', 'parcelas_restantes': 6, 'total_parcelas': 7, 'limite_disponivel': '20.000,00', 'emprestimos_ativos': 1, 'detalhes': [{'valor': '70.000,00', 'vencimento': '12/02/2026'}]},
    ]

@app.route('/')
def principal():
    # Se não estiver logado, manda pro login
    if 'usuario_logado' not in session:
        return redirect(url_for('login'))

    # Se o perfil for de cliente, preparamos os dados para o painel personalizado
    if session.get('perfil') == 'cliente':
        # 1. Obter dados do cliente logado
        id_cliente_logado = session.get('cliente_id')
        dados_clientes = _obter_dados_clientes_completos()
        cliente_atual = next((c for c in dados_clientes if c['id'] == id_cliente_logado), None)

        if not cliente_atual:
            # Caso não encontre o cliente (pouco provável), mostra painel padrão
            return render_template('estrutura/dashboard.html')

        # 2. Realizar os cálculos necessários
        valor_parcela_float = parse_currency(cliente_atual['valor_parcela'])
        parcelas_restantes = cliente_atual['parcelas_restantes']
        total_parcelas = cliente_atual['total_parcelas']
        
        parcelas_pagas = total_parcelas - parcelas_restantes
        saldo_devedor_float = valor_parcela_float * parcelas_restantes
        valor_pago_float = valor_parcela_float * parcelas_pagas
        valor_total_float = valor_pago_float + saldo_devedor_float
        
        percentual_pago = (valor_pago_float / valor_total_float * 100) if valor_total_float > 0 else 0
        
        # Lógica para o Prazo de Pagamento (Countdown)
        data_vencimento_str = cliente_atual['detalhes'][0]['vencimento']
        data_vencimento = datetime.strptime(data_vencimento_str, '%d/%m/%Y').date()
        hoje = datetime.now().date()
        dias_restantes = (data_vencimento - hoje).days
        
        if dias_restantes < 0:
            # Formato: 'Venceu em: DD/MM/AAAA (há X dias)'
            prazo_texto = f"Venceu em: <b>{data_vencimento_str}</b> (há {abs(dias_restantes)} dias)"
        elif dias_restantes == 0:
            prazo_texto = f"Vence em: <b>{data_vencimento_str}</b> (Hoje)"
        else:
            prazo_texto = f"Vence em: <b>{data_vencimento_str}</b> (faltam {dias_restantes} dias)"

        # 3. Preparar dados para o Gráfico de Histórico de Pagamentos
        # Esta é uma simulação simples para fins visuais. Em um sistema real, isso viria do banco.
        # A lógica aqui é apenas para demonstrar as diferentes cores e status.
        historico_chart_data = {
            'labels': ['Jul/25', 'Ago/25', 'Set/25', 'Out/25', 'Nov/25', 'Dez/25'],
            'datasets': [
                {
                    'label': 'Valor Pago',
                    'data': [
                        valor_parcela_float, # Exemplo de pagamento antecipado
                        valor_parcela_float, # Exemplo de pagamento em dia
                        valor_parcela_float, # Exemplo de pagamento em dia
                        valor_parcela_float, # Parcela do mês atual
                        0,                   # Parcela futura
                        0                    # Parcela futura
                    ],
                    # O status de cada barra é usado pelo JavaScript para definir as cores
                    'status': ['pago_antecipado', 'pago_em_dia', 'pago_em_dia', 'atual', 'futuro', 'futuro']
                }
            ]
        }

        


        # 4. Montar o dicionário com todos os dados para a página
        dados_dashboard = {
            'saldo_devedor': formatar_valor_moeda(saldo_devedor_float),
            'limite_disponivel': cliente_atual.get('limite_disponivel', '0,00'),
            'emprestimos_ativos': cliente_atual.get('emprestimos_ativos', 0),
            'prazo_pagamento': prazo_texto,
            'total_emprestimo': formatar_valor_moeda(valor_total_float),
            'total_pago': formatar_valor_moeda(valor_pago_float),
            'percentual_pago': int(percentual_pago),
            'proxima_parcela_valor': formatar_valor_moeda(valor_parcela_float),
            'proxima_parcela_data': cliente_atual['detalhes'][0]['vencimento'],
            'grafico_progresso': {
                'pago': valor_pago_float,
                'restante': saldo_devedor_float
            },
            'historico_chart': historico_chart_data,
            'esta_atrasado': dias_restantes < 0
        }

        return render_template('estrutura/dashboardclientes.html', dados_dashboard=dados_dashboard)

    # --- DADOS E CÁLCULOS PARA O DASHBOARD DO GERENTE ---
    # 1. Fonte de dados única para os clientes do gerente, garantindo consistência.
    dados_clientes_gerente = [
        {'nome': 'João', 'emprestado': 30000, 'recebido': 28000, 'status': 'Em Dia'},
        {'nome': 'Maria', 'emprestado': 25000, 'recebido': 22000, 'status': 'Em Dia'},
        {'nome': 'José', 'emprestado': 45000, 'recebido': 40000, 'status': 'Em Dia'},
        {'nome': 'Carlos', 'emprestado': 20000, 'recebido': 18000, 'status': 'Atrasado'},
        {'nome': 'Fernanda', 'emprestado': 5000, 'recebido': 4500, 'status': 'Em Dia'},
        {'nome': 'Aline', 'emprestado': 70000, 'recebido': 65000, 'status': 'Em Dia'},
        {'nome': 'Roberto', 'emprestado': 5000, 'recebido': 4800, 'status': 'Em Dia'},
    ]
    
    # 2. Gerar dados para o gráfico comparativo a partir da fonte única
    comparativo_chart_data = {
        'labels': [c['nome'] for c in dados_clientes_gerente],
        'datasets': [
            {
                'label': 'Valor Emprestado',
                'data': [c['emprestado'] for c in dados_clientes_gerente]
            },
            {
                'label': 'Valor Recebido',
                'data': [c['recebido'] for c in dados_clientes_gerente]
            }
        ]
    }

    # 3. Gerar dados para os cards de resumo
    total_emprestado = sum(c['emprestado'] for c in dados_clientes_gerente)
    recebimentos_mes_simulado = sum([8000, 5000, 10000, 12000]) # Simulação mantida para este card
    qtd_atrasados = sum(1 for c in dados_clientes_gerente if c['status'] == 'Atrasado')
    taxa_atraso = int((qtd_atrasados / len(dados_clientes_gerente)) * 100) if dados_clientes_gerente else 0

    resumo_gerente = {
        'total_emprestado': formatar_valor_moeda(total_emprestado),
        'recebimentos_mes': formatar_valor_moeda(recebimentos_mes_simulado),
        'disponibilidade_caixa': 'R$ 55.000,00', # Esse mantivemos fixo conforme pedido
        'taxa_atraso': f"{taxa_atraso}%"
    }

    # 4. (NOVO) Gerar dados para os outros gráficos do gerente
    
    # 4.1. Gráfico de Situação de Pagamentos (Doughnut)
    valor_em_dia = sum(c['emprestado'] for c in dados_clientes_gerente if c['status'] == 'Em Dia')
    valor_atrasado = sum(c['emprestado'] for c in dados_clientes_gerente if c['status'] == 'Atrasado')
    valor_quitado_simulado = 30000 # Valor simulado para representar empréstimos já finalizados
    
    situacao_chart_data = {
        'labels': ['Em Dia', 'Atrasados', 'Quitados'],
        'datasets': [{
            'data': [valor_em_dia, valor_atrasado, valor_quitado_simulado],
        }]
    }

    # 4.2. Gráfico de Previsão de Entradas (Line)
    previsao_chart_data = {
        'labels': ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"],
        'datasets': [{
            'label': "Previsão de Entradas",
            'data': [25000, 28000, 30000, 32000, 35000, 38000]
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

    # Se for gerente, apenas renderiza o painel padrão
    return render_template('estrutura/dashboard.html', dados_dashboard={
        'comparativo_chart': comparativo_chart_data,
        'resumo': resumo_gerente,
        'situacao_chart': situacao_chart_data,
        'previsao_chart': previsao_chart_data,
        'lucro_chart': lucro_chart_data
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
