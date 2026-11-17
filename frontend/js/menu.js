const menuButton = document.getElementById("menu_button");
const menu = document.getElementById("menu");

menuButton.addEventListener("click", function () {
    menu.classList.toggle("otwarte");

    
    const otwarte = menu.classList.contains("otwarte");

    menuButton.setAttribute("aria-expanded", otwarte);
    menuButton.setAttribute(
        "aria-label",
        otwarte ? "Zamknij menu" : "Otwórz menu"
    );
});