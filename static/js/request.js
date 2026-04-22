document.getElementById("requestForm").addEventListener("submit", async function(e) {
    e.preventDefault();

    const token = localStorage.getItem("token");

    const subject = document.getElementById("subject").value;
    const message = document.getElementById("message").value;

    try {
        const res = await fetch("/api/requests", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            },
            body: JSON.stringify({
                subject: subject,
                message: message
            })
        });

        const data = await res.json();

        if (data.error) {
            alert(data.error);
            return;
        }

        alert("Request submitted successfully ✅");
        this.reset();

    } catch (err) {
        console.error(err);
        alert("Failed to submit request");
    }
});