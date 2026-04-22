document.addEventListener("DOMContentLoaded", () => {

    const token = localStorage.getItem("token");
    if (!token) {
        window.location.href = "/login";
        return;
    }

    // logout
    document.getElementById("logoutBtn").addEventListener("click", () => {
        localStorage.removeItem("token");
        window.location.href = "/login";
    });

    // dark mode (future extension)
    document.getElementById("darkToggle").addEventListener("change", (e) => {
        document.body.classList.toggle("dark", e.target.checked);
    });

});
