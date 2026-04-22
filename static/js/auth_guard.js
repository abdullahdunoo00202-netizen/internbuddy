function protectDashboard(expectedRole) {
    const token = localStorage.getItem("token");

    if (!token) {
        window.location.href = "/auth";
        return;
    }

    fetch(`/api/dashboard/${expectedRole}`, {
        headers: {
            "Authorization": `Bearer ${token}`
        }
    })
    .then(res => {
        if (!res.ok) throw new Error("Unauthorized");
        return res.json();
    })
    .catch(() => {
        localStorage.removeItem("token");
        window.location.href = "/auth";
    });
}
