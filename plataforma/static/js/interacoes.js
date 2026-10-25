const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

document.addEventListener("click", async (evento) => {
    // pega o botão clicado (favoritar ou votar)
    const botao = evento.target.closest("[data-acao]");
    if (!botao) return;

    // avisa o servidor
    const resposta = await fetch(botao.dataset.url, {
        method: "POST",
        headers: { "X-CSRFToken": csrfToken },
    });

    // não está logado: manda para o login
    if (resposta.status === 401) {
        const dados = await resposta.json();
        window.location.href = dados.login_url;
        return;
    }

    if (!resposta.ok) return;

    const dados = await resposta.json();

    // atualiza todos os botões da mesma oferta
    // (a mesma oferta pode aparecer em mais de uma seção da home)
    document.querySelectorAll('[data-url="' + botao.dataset.url + '"]').forEach((b) => {
        b.classList.toggle("is-active", dados.ativo);
        b.setAttribute("aria-pressed", dados.ativo);

        if (b.dataset.acao === "favoritar") {
            b.textContent = dados.ativo ? "♥" : "♡";
        }

        if (b.dataset.acao === "votar") {
            b.querySelector("[data-votos]").textContent = dados.total;
        }
    });
});