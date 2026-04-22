document.addEventListener("DOMContentLoaded", loadInterns);

async function loadInterns() {
    const token = localStorage.getItem("token");

    const res = await fetch("/api/manager/accepted", {
        headers: { Authorization: "Bearer " + token }
    });

    const data = await res.json();

    const grid = document.getElementById("internsGrid");
    grid.innerHTML = "";

    if (!data || data.length === 0) {
        grid.innerHTML = "<p>No active interns</p>";
        return;
    }

    data.forEach(o => {
        const card = document.createElement("div");
        card.className = "application-card";

        card.innerHTML = `
            <h4>${o.domain.toUpperCase()} Intern</h4>
            <p><strong>Manager:</strong> ${o.manager}</p>
            <p class="status-active">Active</p>
        `;

        grid.appendChild(card);
    });
}