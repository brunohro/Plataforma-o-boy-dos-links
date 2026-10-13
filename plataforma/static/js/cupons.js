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

            setTimeout(() => {
                texto.textContent = "Copiar";
                icone.className = "fa-regular fa-copy";
                button.classList.remove("is-copied");
            }, 1800);
        } catch (error) {
            window.prompt("Copie o código do cupom:", codigo);
        }
    });
});