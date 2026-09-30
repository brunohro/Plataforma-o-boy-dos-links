const animacaoAba = [
    {
        titulo: "🛒 O Boy dos Links",
        favicon: "/static/images/favicon-1.png"
    },
    {
        titulo: "🔥 OFERTA NOVA!",
        favicon: "/static/images/favicon-2.png"
    },
    {
        titulo: "💰 DESCONTO!",
        favicon: "/static/images/favicon-3.png"
    }
];

let indice = 0;

function animarAba() {
    document.title = animacaoAba[indice].titulo;

    document.getElementById("favicon").href =
        animacaoAba[indice].favicon;

    indice = (indice + 1) % animacaoAba.length;
}

animarAba();

setInterval(animarAba, 2000);