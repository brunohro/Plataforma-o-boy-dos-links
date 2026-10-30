function getCookie(name) {
    const match = document.cookie.match(new RegExp("(^|;\\s*)" + name + "=([^;]*)"));
    return match ? decodeURIComponent(match[2]) : "";
}

// Conta o uso no servidor (funciona para logado e anônimo)
async function registrarCopia(button) {
    const url = button.dataset.copyUrl;
    if (!url) return;

    try {
        const resposta = await fetch(url, {
            method: "POST",
            headers: { "X-CSRFToken": getCookie("csrftoken") },
            credentials: "same-origin",
        });
        if (!resposta.ok) return;

        const dados = await resposta.json();
        document
            .querySelectorAll(`[data-uses-for="${button.dataset.cupomId}"]`)
            .forEach((el) => (el.textContent = dados.usos));
    } catch (erro) {
        console.error("Não foi possível registrar a cópia do cupom", erro);
    }
}

document.querySelectorAll(".coupon-card__copy").forEach((button) => {
    button.addEventListener("click", async () => {
        const codigo = button.dataset.code;
        const texto = button.querySelector("span");
        const icone = button.querySelector("i");

        try {
            await navigator.clipboard.writeText(codigo);

            texto.textContent = "Copiado!";
            icone.className = "fa-solid fa-check";
            button.classList.add("is-copied");

            registrarCopia(button);

            setTimeout(() => {
                texto.textContent = "Copiar";
                icone.className = "fa-regular fa-copy";
                button.classList.remove("is-copied");
            }, 1800);
        } catch (error) {
            window.prompt("Copie o código do cupom:", codigo);
            registrarCopia(button);
        }
    });
});