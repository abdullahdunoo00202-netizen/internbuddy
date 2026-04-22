document.addEventListener("DOMContentLoaded", loadOffers);

async function loadOffers() {
    const token = localStorage.getItem("token");

    try {
        const res = await fetch("/api/student-offers", {
            headers: { Authorization: "Bearer " + token }
        });

        const data = await res.json();
        renderOffers(data.offers);

    } catch (err) {
        console.error("Error loading offers:", err);
    }
}

function renderOffers(offers) {
    const grid = document.getElementById("offersGrid");
    grid.innerHTML = "";

    if (!offers || offers.length === 0) {
        grid.innerHTML = "<p>No offers available</p>";
        return;
    }

    offers.forEach(o => {
        const card = document.createElement("div");
        card.className = "offer-card-box";

        let actions = "";

        // 🔥 PENDING STATE
        if (o.status === "pending") {
            actions = `
                <div class="offer-btns">
                    <button class="btn-accept" onclick="handleOffer('${o._id}', 'accepted')">
                        Accept
                    </button>

                    <button class="btn-reject" onclick="handleOffer('${o._id}', 'rejected')">
                        Reject
                    </button>
                </div>
            `;
        }

        // 🔥 ACCEPTED STATE (MAIN FEATURE)
        if (o.status === "accepted") {
            actions = `
                <div class="accepted-box">
                    <p class="accepted-text">
                        🎉 You are accepted for the internship!
                    </p>

                    <p class="accepted-sub">
                        Your credentials have been sent to your email.
                        Please check your email to access your LMS account.
                    </p>

                    <a href="https://internbuddy-lms.onrender.com" target="_blank" class="lms-btn">
                        Go to LMS
                    </a>
                </div>
            `;
        }

        // 🔥 REJECTED STATE (optional but clean UX)
        if (o.status === "rejected") {
            actions = `
                <div class="accepted-box" style="border-color:#ff4d4d; background:rgba(255,0,0,0.08)">
                    <p class="accepted-text" style="color:#ff6b6b">
                        ❌ You rejected this offer
                    </p>
                </div>
            `;
        }

        card.innerHTML = `
            <h4>${o.domain.toUpperCase()} Internship</h4>
            <p><strong>Duration:</strong> ${o.duration}</p>
            <p><strong>Manager:</strong> ${o.manager_name}</p>
            <p class="status"><strong>Status:</strong> ${o.status}</p>

            ${actions}
        `;

        grid.appendChild(card);
    });
}

async function handleOffer(id, action) {
    const token = localStorage.getItem("token");

    try {
        await fetch(`/api/offer-action/${id}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            },
            body: JSON.stringify({ action })
        });

        // 🔥 UI REFRESH
        loadOffers();

    } catch (err) {
        console.error("Error updating offer:", err);
    }
}