document.addEventListener("DOMContentLoaded", loadRequests);

async function loadRequests() {
    const res = await fetch("/api/manager/requests");
    const data = await res.json();

    const grid = document.getElementById("requestsGrid");
    grid.innerHTML = "";

    data.forEach(r => {
        const card = document.createElement("div");
        card.className = "application-card";

        card.innerHTML = `
            <h4>${r.subject}</h4>
            <p><strong>${r.name}</strong> (${r.email})</p>
            <p>${r.message}</p>
            <p>Status: ${r.status}</p>
        `;

        grid.appendChild(card);
    });
}