(function () {
    "use strict";

    var INTERVALO = 5000;

    document.querySelectorAll("[data-carousel]").forEach(function (carrossel) {
        var track = carrossel.querySelector(".carousel-track");
        var slides = carrossel.querySelectorAll(".carousel-slide");
        var pontos = carrossel.querySelectorAll("[data-carousel-dot]");
        var anterior = carrossel.querySelector("[data-carousel-prev]");
        var proximo = carrossel.querySelector("[data-carousel-next]");

        // Um só banner: nada para girar
        if (!track || slides.length < 2) {
            return;
        }

        var atual = 0;
        var timer = null;
        var semMovimento = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

        function mostrar(numero) {
            atual = (numero + slides.length) % slides.length;
            track.style.transform = "translateX(-" + atual * 100 + "%)";

            pontos.forEach(function (ponto, indice) {
                ponto.classList.toggle("active", indice === atual);
            });
        }

        function parar() {
            if (timer) {
                clearInterval(timer);
                timer = null;
            }
        }

        function iniciar() {
            parar();
            if (!semMovimento) {
                timer = setInterval(function () {
                    mostrar(atual + 1);
                }, INTERVALO);
            }
        }

        if (anterior) {
            anterior.addEventListener("click", function () {
                mostrar(atual - 1);
                iniciar();
            });
        }

        if (proximo) {
            proximo.addEventListener("click", function () {
                mostrar(atual + 1);
                iniciar();
            });
        }

        pontos.forEach(function (ponto) {
            ponto.addEventListener("click", function () {
                mostrar(Number(ponto.dataset.carouselDot));
                iniciar();
            });
        });

        // Pausa enquanto a pessoa está lendo
        carrossel.addEventListener("mouseenter", parar);
        carrossel.addEventListener("mouseleave", iniciar);
        carrossel.addEventListener("focusin", parar);
        carrossel.addEventListener("focusout", iniciar);

        iniciar();
    });
})();
