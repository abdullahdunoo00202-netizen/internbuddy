document.addEventListener("DOMContentLoaded", loadAccepted);

async function loadAccepted() {
    const token = localStorage.getItem("token");

    const res = await fetch("/api/manager/accepted", {
        headers: { Authorization: "Bearer " + token }
    });

    const data = await res.json();

    const grid = document.getElementById("acceptedGrid");
    grid.innerHTML = "";

    if (!data || data.length === 0) {
        grid.innerHTML = "<p>No accepted students</p>";
        return;
    }

    data.forEach(o => {
        const card = document.createElement("div");
        card.className = "application-card";

        card.innerHTML = `
            <h4>${o.domain.toUpperCase()} Internship</h4>
            <p><strong>Manager:</strong> ${o.manager}</p>
        `;

        grid.appendChild(card);
    });
}