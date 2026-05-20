// Máscara para Telefone Celular, essa função vai ficar ouvindo todo o Front, e se encontrar uma classe específica vai aplicar a máscara de telefone
function mascaraTelefoneCelular() {
    // Função para aplicar a máscara no valor do input
    function aplicarMascaraTelefone(valor) {
        valor = valor.replace(/\D/g, ""); // Removendo caracteres não numéricos
        valor = valor.replace(/^(\d{2})(\d)/, "($1) $2"); // Adicionando parênteses ao DDD 
        valor = valor.replace(/(\d{5})(\d)/, "$1-$2");// Adicionando o traço
        return valor.slice(0, 15); // Limitando o tamanho máx.
    }


    // Selecionar todos os Inputs que tiver classe 'mascara-telefone-celular celular'
    const inputsTelefoneCelular = document.querySelectorAll(".mascara-telefone-celular");

    // Aplicando o evento de Input para cada campo que tiver a classe
    inputsTelefoneCelular.forEach((input) => {
        input.addEventListener("input", (e) => {
            e.target.value = aplicarMascaraTelefone(e.target.value);
        });
    });

}

// Função para permitir apenas letras e espaços (bloqueia números e símbolos)
function mascaraSomenteLetras() {
    const inputsSomenteLetras = document.querySelectorAll(".somente-letras");
    inputsSomenteLetras.forEach((input) => {
        input.addEventListener("input", (e) => {
            e.target.value = e.target.value.replace(/[^a-zA-ZÀ-ÿ\s]/g, "");
        });
    });
}

// Função para buscar cores definidas no CSS (centraliza a identidade visual)
function pegarCorDoCSS(nomeDaVariavel) {
    // Alterado para document.body para detectar mudanças de classe (ex: dark-mode)
    return getComputedStyle(document.body).getPropertyValue(nomeDaVariavel).trim();
}

// Função para exibir notificações de sucesso de forma padronizada
function notificarSucesso(titulo, mensagem) {
    $.notify({
        icon: 'fa fa-check',
        title: titulo,
        message: mensagem,
    }, {
        type: 'success',
        placement: { from: 'top', align: 'right' },
        time: 1000
    });
}

// Função para alternar entre o Modo Claro e o Modo Escuro
function alternarTema() {
    const body = document.body;
    const icone = document.getElementById('icone-tema');

    // Toggle: se a classe não existe, ele coloca. Se existe, ele tira.
    body.classList.toggle('dark-mode');

    // Salva a escolha no navegador e troca o ícone
    if (body.classList.contains('dark-mode')) {
        icone.classList.replace('fa-moon', 'fa-sun');
        localStorage.setItem('tema-preferido', 'escuro');
    } else {
        icone.classList.replace('fa-sun', 'fa-moon');
        localStorage.setItem('tema-preferido', 'claro');
    }

}

// Função para verificar se o usuário já tinha escolhido o modo escuro antes
function verificarTemaSalvo() {
    const temaSalvo = localStorage.getItem('tema-preferido');
    if (temaSalvo === 'escuro') {
        document.body.classList.add('dark-mode');
        const icone = document.getElementById('icone-tema');
        if (icone) icone.classList.replace('fa-moon', 'fa-sun');
    }
}

// Executa a verificação IMEDIATAMENTE para garantir que a classe 'dark-mode' 
// esteja no body antes de qualquer script de gráfico rodar.
verificarTemaSalvo();

function iniciarRelogio() {
    function atualizar() {
        const agora = new Date();
        const h = String(agora.getHours()).padStart(2, '0');
        const m = String(agora.getMinutes()).padStart(2, '0');
        const s = String(agora.getSeconds()).padStart(2, '0');
        const display = document.getElementById('relogio-digital');
        if (display) {
            display.textContent = `${h}:${m}:${s}`;
        }
    }
    setInterval(atualizar, 1000); // Faz o relógio atualizar a cada 1 segundo
    atualizar(); // Chama uma vez na hora para não começar em 00:00:00
}

// Inicializador de Funções
function inicializar() {
    mascaraTelefoneCelular();
    mascaraSomenteLetras();
    iniciarRelogio(); // Ativa o relógio assim que a página carrega
}

window.addEventListener('load', inicializar);
