(function () {
    "use strict";

    const canvas = document.getElementById("grafico-adm");
    const seletor = document.getElementById("grafico-dias");
    const botoes = document.querySelectorAll(".period-button[data-agrupar]");
    const aviso = document.getElementById("grafico-vazio");
    const container = document.querySelector(".chart-canvas-wrap");

    if (!canvas || !seletor || !container || typeof Chart === "undefined") {
        return;
    }

    const urlDados = container.dataset.url;

    // Cores vindas das variáveis CSS do site (com valor padrão de reserva)
    const estilos = getComputedStyle(document.documentElement);
    const cor = (variavel, padrao) => estilos.getPropertyValue(variavel).trim() || padrao;
    const corVisitas = cor("--primary", "#f97316");
    const corCliques = cor("--warning", "#eab308");
    const corTexto = cor("--text-secondary", "#9ca3af");
    const corGrade = cor("--border", "#333333");

    let agrupar = "dia";
    let grafico = null;

    function montar(dados) {
        const config = {
            type: "line",
            data: {
                labels: dados.labels,
                datasets: [
                    {
                        label: "Visitas",
                        data: dados.visitas,
                        borderColor: corVisitas,
                        backgroundColor: corVisitas,
                        tension: 0.3,
                        pointRadius: 2
                    },
                    {
                        label: "Cliques",
                        data: dados.cliques,
                        borderColor: corCliques,
                        backgroundColor: corCliques,
                        tension: 0.3,
                        pointRadius: 2
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: "index", intersect: false },
                plugins: { legend: { display: false } },
                scales: {
                    x: { ticks: { color: corTexto, maxTicksLimit: 10 }, grid: { display: false } },
                    y: { beginAtZero: true, ticks: { color: corTexto, precision: 0 }, grid: { color: corGrade } }
                }
            }
        };

        if (grafico) {
            grafico.destroy();
        }
        grafico = new Chart(canvas, config);
    }

    async function carregar() {
        try {
            const resposta = await fetch(
                `${urlDados}?dias=${seletor.value}&agrupar=${agrupar}`,
                { credentials: "same-origin" }
            );
            if (!resposta.ok) {
                throw new Error("Falha ao carregar o gráfico");
            }
            const dados = await resposta.json();
            const total = dados.visitas.concat(dados.cliques).reduce((a, b) => a + b, 0);
            if (aviso) {
                aviso.hidden = total > 0;
            }
            montar(dados);
        } catch (erro) {
            console.error(erro);
        }
    }

    botoes.forEach(function (botao) {
        botao.addEventListener("click", function () {
            botoes.forEach(function (b) { b.classList.remove("active"); });
            botao.classList.add("active");
            agrupar = botao.dataset.agrupar;
            carregar();
        });
    });

    seletor.addEventListener("change", carregar);

    carregar();
})();