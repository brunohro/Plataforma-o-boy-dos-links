let slideAtual = 0;

const slides = document.querySelectorAll(".carousel-slide");
const track = document.querySelector(".carousel-track");
const indicadores = document.querySelectorAll(".indicator");

function mostrarSlide(numero) {

    if (numero >= slides.length) {
        slideAtual = 0;
    }

    else if (numero < 0) {
        slideAtual = slides.length - 1;
    }

    else {
        slideAtual = numero;
    }

    track.style.transform = `translateX(-${slideAtual * 100}%)`;

    indicadores.forEach((indicador, index) => {

        indicador.classList.toggle(
            "active",
            index === slideAtual
        );

    });
}


function mudarSlide(direcao) {

    mostrarSlide(slideAtual + direcao);

}


function irParaSlide(numero) {

    mostrarSlide(numero);

}


/* Troca automática */

setInterval(() => {

    mudarSlide(1);

}, 5000);