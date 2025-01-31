document.addEventListener("DOMContentLoaded", function () {
    let sections = document.querySelectorAll("section");
    let scrollTopBtn = document.createElement("button");

    // Configuración del botón "Subir al inicio"
    scrollTopBtn.id = "scrollTopBtn";
    scrollTopBtn.innerHTML = "⬆";
    document.body.appendChild(scrollTopBtn);

    function revealOnScroll() {
        sections.forEach((section) => {
            let sectionTop = section.getBoundingClientRect().top;
            let windowHeight = window.innerHeight;

            if (sectionTop < windowHeight - 50) {
                section.classList.add("visible");
            }
        });

        // Mostrar el botón "Subir" cuando el usuario hace scroll hacia abajo
        if (window.scrollY > 300) {
            scrollTopBtn.style.display = "block";
        } else {
            scrollTopBtn.style.display = "none";
        }
    }

    // Evento para subir al inicio al hacer clic en el botón
    scrollTopBtn.addEventListener("click", function () {
        window.scrollTo({ top: 0, behavior: "smooth" });
    });

    window.addEventListener("scroll", revealOnScroll);
    revealOnScroll(); // Para mostrar las secciones ya visibles al cargar
});
