document.addEventListener("DOMContentLoaded", async () => {

    const token = localStorage.getItem("token");
    if (!token) {
        window.location.href = "/login";
        return;
    }

    document.getElementById("logoutBtn").onclick = () => {
        localStorage.removeItem("token");
        window.location.href = "/login";
    };

    try {
        const res = await fetch("/manager/api/applied-students", {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        const data = await res.json();
        const table = document.getElementById("appliedTable");
        table.innerHTML = "";

        if (!data.length) {
            table.innerHTML =
                "<tr><td colspan='9'>No applications found</td></tr>";
            return;
        }

        data.forEach((app, index) => {
            const row = document.createElement("tr");

            row.innerHTML = `
                <td>${index + 1}</td>
                <td>${app.name}</td>
                <td>${app.email}</td>
                <td>${app.cgpa}</td>
                <td>${app.domain}</td>
                <td>${app.resume_match}%</td>
                <td>${app.status}</td>
                <td>
                    <a href="/uploads/${app.resume}" target="_blank">View</a>
                </td>
                <td>
                    <button onclick="updateStatus('${app.id}', 'approved')">Approve</button>
                    <button onclick="updateStatus('${app.id}', 'rejected')">Reject</button>
                </td>
            `;

            table.appendChild(row);
        });

    } catch (err) {
        console.error(err);
    }
});

async function updateStatus(id, status) {
    const token = localStorage.getItem("token");

    await fetch(`/manager/api/update-status/${id}`, {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ status })
    });

    location.reload();
}
