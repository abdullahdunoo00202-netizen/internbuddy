console.log("JS LOADED");

/* ================= INIT ================= */
/* ================= INIT ================= */
document.addEventListener("DOMContentLoaded", async () => {
    const token = localStorage.getItem("token");

    if (!token) {
        window.location.href = "/login";
        return;
    }

    try {
        const res = await fetch("/api/my-applications", {
            headers: { Authorization: `Bearer ${token}` }
        });

        const data = await res.json();
        console.log("MY APPLICATIONS DATA:", data);

        /* ===== SAFE DATA HANDLING ===== */
        let student = null;
        let applications = [];

        // Case 1: Proper object response
        if (data.student && data.applications) {
            student = data.student;
            applications = data.applications;
        }
        // Case 2: Only applications array
        else if (Array.isArray(data)) {
            applications = data;
        }
        // Case 3: fallback (unexpected structure)
        else {
            applications = data.applications || [];
            student = data.student || null;
        }

        /* ===== LOAD DATA ===== */
        loadProfile(student);
        renderApplications(applications);

    } catch (err) {
        console.error("ERROR:", err);
        alert("Failed to load data");
    }
});

/* ================= PROFILE ================= */
function loadProfile(student) {
    if (!student) return;

    document.getElementById("studentName").innerText = student.name || "—";
    document.getElementById("studentEmail").innerText = student.email || "N/A";
    document.getElementById("studentCgpa").innerText = student.cgpa || "N/A";

    if (student.profile_picture) {
        document.getElementById("profilePic").src =
            `/uploads/${student.profile_picture}`;
    }
}


/* ================= APPLICATION CARDS ================= */
function renderApplications(applications) {
    const grid = document.getElementById("applicationsGrid");
    grid.innerHTML = "";

    if (!applications || applications.length === 0) {
        grid.innerHTML = "<p>No internship applications found.</p>";
        return;
    }

    applications.forEach(app => {
        const card = document.createElement("div");
        card.className = "application-card";

        const match = Number(app.resume_match || 0);
        const testStatus = app.test_status || "not_started";

        card.innerHTML = `
            <h4>${(app.domain || "General").toUpperCase()} Internship</h4>
            <p>Status: <span class="status-text">${testStatus}</span></p>
            <p><strong>Resume Match:</strong> ${match.toFixed(1)}%</p>
        `;

        /* ===== TEST BUTTON ===== */
        if (app.status === "slot_selected") {
            const button = document.createElement("button");
            button.className = "start-test-btn";

            const isCompleted = testStatus === "completed";

            button.innerText = isCompleted ? "Test Completed" : "▶ Start Test";
            button.disabled = isCompleted;

            if (!isCompleted) {
                button.onclick = () => startTest(app._id, button);
            }

            card.appendChild(button);
        }

        /* ===== SLOT SELECTION ===== */
        if (app.status === "approved") {
            const section = document.createElement("div");
            section.className = "slot-section";

            section.innerHTML = `
                <h3>Select Assessment Slot</h3>

                <input type="date"
                       id="slotDate-${app._id}"
                       onchange="loadSlots('${app._id}')">

                <select id="slotTime-${app._id}">
                    <option value="">Select Time</option>
                </select>

                <button onclick="bookSlot('${app._id}', this)">
                    Confirm Slot
                </button>

                <!-- ✅ PROFESSIONAL RULES BOX -->
                <div class="rules-box">
                    <h4><i class="fas fa-shield-alt"></i> Assessment Rules</h4>
                    <ul>
                        <li>Camera & microphone must remain ON</li>
                        <li>Face must stay visible and centered</li>
                        <li>No tab switching or exiting fullscreen</li>
                        <li>No external help or voice assistance allowed</li>
                        <li>Suspicious activity may cancel your test</li>
                    </ul>
                </div>
            `;

            card.appendChild(section);
        }

        grid.appendChild(card);
    });
}


async function loadSlots(appId) {
    const token = localStorage.getItem("token");

    let date = document.getElementById(`slotDate-${appId}`).value;

    if (!date) return;

    console.log("DATE SENT TO API:", date);

    const select = document.getElementById(`slotTime-${appId}`);

    try {
        const res = await fetch(`/api/slots/${date}`, {
            headers: { Authorization: `Bearer ${token}` }
        });

        const slots = await res.json();

        console.log("SLOTS:", slots);

        select.innerHTML = "<option value=''>Select Time</option>";

        if (!slots || slots.length === 0) {
            select.innerHTML = "<option>No slots available</option>";
            return;
        }

        slots.forEach(s => {
            const opt = document.createElement("option");
            opt.value = s._id;
            opt.textContent = s.time;
            opt.disabled = !s.available;
            select.appendChild(opt);
        });

    } catch (err) {
        console.error("Slot load error:", err);
    }
}
/* ================= BOOK SLOT ================= */
function bookSlot(applicationId, btn) {
    const token = localStorage.getItem("token");
    const slotId = document.getElementById(`slotTime-${applicationId}`).value;

    if (!slotId) {
        alert("Select time first");
        return;
    }

    btn.disabled = true;

    fetch(`/api/select-slot/${applicationId}`, {   // ✅ correct
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ slot_id: slotId })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
            btn.disabled = false;
            return;
        }

        alert("Slot booked successfully ✅");
        location.reload();   // ✅ UI refresh
    })
    .catch(() => {
        alert("Booking failed ❌");
        btn.disabled = false;
    });
}
/* ================= START TEST ================= */
function startTest(applicationId, button) {
    const token = localStorage.getItem("token");

    fetch(`/start-test/${applicationId}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        }
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
            return;
        }

        // Disable button
        button.disabled = true;
        button.innerText = "Test Completed";

        // Redirect to proctor (IMPORTANT)
        window.location.href = data.proctor_url;
    })
    .catch(err => {
        console.error("Error:", err);
    });
}


function viewOffers() {
    window.location.href = "/student/offers";
}

function sendRequest() {
    window.location.href = "/student/request";
}