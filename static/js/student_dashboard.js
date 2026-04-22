const token = localStorage.getItem("token");

// 🔐 JWT protection
if (!token) {
    window.location.href = "/login";
}

// DOM Elements
const logoutBtn = document.getElementById("logoutBtn");

// ================= LOGOUT =================
if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
        localStorage.removeItem("token");
        window.location.href = "/login";
    });
}

/* ======================================================
   ✅ APPLY LIMIT CHECK (STABLE VERSION – NO 404)
   ====================================================== */
async function checkApplicationLimit() {
    const token = localStorage.getItem("token");

    try {
        // 🔥 USE RELIABLE ENDPOINT
        const res = await fetch("/api/my-applications", {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (!res.ok) {
            throw new Error("Failed to fetch applications");
        }

        const data = await res.json();
        const appCount = data.applications ? data.applications.length : 0;

        // Update count UI
        const appCountElement = document.getElementById("appCount");
        if (appCountElement) {
            appCountElement.innerText = appCount;
        }

        // Apply limit logic
        if (appCount >= 2) {
            document.querySelectorAll(".apply-link, .domain-apply-btn")
                .forEach(btn => {
                    btn.innerText = "Limit Reached";
                    btn.style.pointerEvents = "none";
                    btn.style.opacity = "0.5";
                    btn.style.cursor = "not-allowed";
                    btn.setAttribute("disabled", "true");
                });
        } else {
            document.querySelectorAll(".apply-link, .domain-apply-btn")
                .forEach(btn => {
                    if (btn.href && btn.href.includes("/apply/")) {
                        btn.innerText = btn.classList.contains("apply-link")
                            ? "Apply Now"
                            : "Apply";
                        btn.style.pointerEvents = "auto";
                        btn.style.opacity = "1";
                        btn.style.cursor = "pointer";
                        btn.removeAttribute("disabled");
                    }
                });
        }

    } catch (error) {
        console.error("Application limit check failed:", error);
        const appCountElement = document.getElementById("appCount");
        if (appCountElement) appCountElement.innerText = "0";
    }
}

// Run on page load
document.addEventListener("DOMContentLoaded", () => {
    checkApplicationLimit();
    setTimeout(checkApplicationLimit, 500);
});

// Periodic refresh
setInterval(checkApplicationLimit, 30000);

/* ======================================================
   ANIMATIONS
   ====================================================== */
const observerOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px"
};

const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add("animate-in");
        }
    });
}, observerOptions);

document.querySelectorAll(
    ".internship-card, .domain-card, .benefit-card, .action-card"
).forEach(el => observer.observe(el));

/* ======================================================
   STYLES (Injected)
   ====================================================== */
const style = document.createElement("style");
style.textContent = `
.internship-card,
.domain-card,
.benefit-card,
.action-card {
    opacity: 0;
    transform: translateY(20px);
    transition: opacity 0.6s ease, transform 0.6s ease;
}
.animate-in {
    opacity: 1;
    transform: translateY(0);
}
.apply-link[disabled],
.domain-apply-btn[disabled] {
    pointer-events: none !important;
    opacity: 0.5 !important;
    cursor: not-allowed !important;
}
`;
document.head.appendChild(style);

/* ======================================================
   STUDENT NAME FROM TOKEN
   ====================================================== */
try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    const nameEl = document.querySelector(".student-name");
    if (payload.name && nameEl) {
        nameEl.textContent = payload.name;
    }
} catch (e) {
    console.log("Token parse failed");
}

/* ======================================================
   HOVER EFFECTS
   ====================================================== */
document.querySelectorAll(".nav-btn, .apply-link, .domain-apply-btn")
    .forEach(btn => {
        if (btn.getAttribute("disabled")) return;

        btn.addEventListener("mouseenter", () => {
            btn.style.transform = "translateY(-2px)";
        });

        btn.addEventListener("mouseleave", () => {
            btn.style.transform = "translateY(0)";
        });
    });

/* ======================================================
   NOTIFICATION SYSTEM
   ====================================================== */
function showNotification(message) {
    const existing = document.querySelector(".custom-notification");
    if (existing) existing.remove();

    const notification = document.createElement("div");
    notification.className = "custom-notification";
    notification.innerHTML = `
        <div style="
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(255,75,75,0.95);
            color: white;
            padding: 15px 20px;
            border-radius: 10px;
            z-index: 9999;
            box-shadow: 0 5px 15px rgba(0,0,0,0.25);
        ">
            ${message}
        </div>
    `;
    document.body.appendChild(notification);

    setTimeout(() => notification.remove(), 5000);
}

/* ======================================================
   CLICK BLOCK FOR DISABLED BUTTONS
   ====================================================== */
document.addEventListener("click", e => {
    const btn = e.target.closest(".apply-link, .domain-apply-btn");
    if (!btn) return;

    if (
        btn.getAttribute("disabled") ||
        btn.style.pointerEvents === "none" ||
        btn.innerText === "Limit Reached"
    ) {
        e.preventDefault();
        showNotification(
            "❌ You have reached the maximum limit of 2 applications. Visit 'My Applications' to manage them."
        );
    }
});

/* ======================================================
   STYLE APPLY BUTTONS
   ====================================================== */
function styleApplyButtons() {
    document.querySelectorAll(".apply-link, .domain-apply-btn")
        .forEach(btn => {
            if (btn.getAttribute("disabled")) return;

            btn.style.borderRadius = "10px";
            btn.style.fontWeight = "600";
            btn.style.transition = "all 0.3s ease";
        });
}

document.addEventListener("DOMContentLoaded", styleApplyButtons);
