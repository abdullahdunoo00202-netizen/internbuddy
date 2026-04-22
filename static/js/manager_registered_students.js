document.addEventListener("DOMContentLoaded", async () => {

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

    try {
        const res = await fetch("/manager/api/registered-students", {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        const students = await res.json();
        const table = document.getElementById("studentsTable");
        table.innerHTML = "";

        if (!students.length) {
            table.innerHTML = "<tr><td colspan='3'>No registered students</td></tr>";
            return;
        }

        students.forEach((student, index) => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${index + 1}</td>
                <td>${student.name}</td>
                <td>${student.email}</td>
            `;
            table.appendChild(row);
        });

    } catch (err) {
        console.error(err);
        document.getElementById("studentsTable").innerHTML =
            "<tr><td colspan='3'>Failed to load data</td></tr>";
    }
});
