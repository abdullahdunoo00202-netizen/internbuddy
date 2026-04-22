document.addEventListener("DOMContentLoaded", loadAssigned);

async function loadAssigned() {
    const token = localStorage.getItem("token");

    const res = await fetch("/api/manager/assigned", {
        headers: { Authorization: "Bearer " + token }
    });

    const data = await res.json();

    const grid = document.getElementById("assignedGrid");
    grid.innerHTML = "";

    if (!data || data.length === 0) {
        grid.innerHTML = "<p>No assigned internships</p>";
        return;
    }

    data.forEach(o => {
        const card = document.createElement("div");
        card.className = "application-card";

        card.innerHTML = `
            <h4>${o.domain.toUpperCase()} Internship</h4>
            <p><strong>Manager:</strong> ${o.manager}</p>
            <p><strong>Status:</strong> ${o.status}</p>
        `;

        grid.appendChild(card);
    });
}