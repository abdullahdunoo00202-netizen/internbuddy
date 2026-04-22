document.addEventListener("DOMContentLoaded", () => {

    // 🔧 FIX: BASE URL (ONLY ADDITION)
    const BASE_URL = "/api/auth";

    // Create animated background particles
    createParticles();
    
    const loginForm = document.getElementById("loginForm");
    const registerForm = document.getElementById("registerForm");
    const showRegister = document.getElementById("showRegister");
    const showLogin = document.getElementById("showLogin");

    // Create alert container
    const alertContainer = document.createElement('div');
    alertContainer.className = 'alert';
    loginForm.parentNode.insertBefore(alertContainer, loginForm);

    // TOGGLE FORMS WITH ANIMATION
    showRegister.onclick = (e) => {
        e.preventDefault();
        loginForm.style.opacity = '0';
        loginForm.style.transform = 'translateX(-20px)';
        
        setTimeout(() => {
            loginForm.classList.add("hidden");
            registerForm.classList.remove("hidden");
            registerForm.style.opacity = '0';
            registerForm.style.transform = 'translateX(20px)';
            
            setTimeout(() => {
                registerForm.style.opacity = '1';
                registerForm.style.transform = 'translateX(0)';
            }, 50);
        }, 300);
    };

    showLogin.onclick = (e) => {
        e.preventDefault();
        registerForm.style.opacity = '0';
        registerForm.style.transform = 'translateX(20px)';
        
        setTimeout(() => {
            registerForm.classList.add("hidden");
            loginForm.classList.remove("hidden");
            loginForm.style.opacity = '0';
            loginForm.style.transform = 'translateX(-20px)';
            
            setTimeout(() => {
                loginForm.style.opacity = '1';
                loginForm.style.transform = 'translateX(0)';
            }, 50);
        }, 300);
    };

    // Show alert message
    function showAlert(message, type = 'error') {
        alertContainer.textContent = message;
        alertContainer.className = `alert ${type}`;
        alertContainer.style.display = 'block';
        
        setTimeout(() => {
            alertContainer.style.display = 'none';
        }, 5000);
    }

    // Show loading state
    function showLoading(button) {
        const originalText = button.innerHTML;
        button.innerHTML = '<div class="loader"></div>';
        button.disabled = true;
        return originalText;
    }

    // Hide loading state
    function hideLoading(button, originalText) {
        button.innerHTML = originalText;
        button.disabled = false;
    }

    // REGISTER
    registerForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const submitBtn = registerForm.querySelector('button[type="submit"]');
        const originalText = showLoading(submitBtn);

        const data = {
            name: document.getElementById("name").value.trim(),
            email: document.getElementById("email").value.trim().toLowerCase(),
            password: document.getElementById("password").value,
            role: document.getElementById("role").value
        };

        if (!data.name || !data.email || !data.password) {
            showAlert('Please fill in all fields', 'error');
            hideLoading(submitBtn, originalText);
            return;
        }

        if (!isValidEmail(data.email)) {
            showAlert('Please enter a valid email address', 'error');
            hideLoading(submitBtn, originalText);
            return;
        }

        if (data.password.length < 8) {
            showAlert('Password must be at least 8 characters', 'error');
            hideLoading(submitBtn, originalText);
            return;
        }

        try {
            const res = await fetch(`${BASE_URL}/register`, { // 🔧 FIX
                method: "POST",
                headers: { 
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                body: JSON.stringify(data)
            });

            const result = await res.json();
            
            if (!res.ok) throw new Error(result.error);

            showAlert(result.message || 'Registration successful!', 'success');
            registerForm.reset();

            setTimeout(() => showLogin.click(), 2000);

        } catch (error) {
            showAlert(error.message || 'Registration failed', 'error');
        } finally {
            hideLoading(submitBtn, originalText);
        }
    });

    // LOGIN
    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const submitBtn = loginForm.querySelector('button[type="submit"]');
        const originalText = showLoading(submitBtn);

        const data = {
            email: document.getElementById("loginEmail").value.trim().toLowerCase(),
            password: document.getElementById("loginPassword").value
        };

        if (!data.email || !data.password) {
            showAlert('Please fill in all fields', 'error');
            hideLoading(submitBtn, originalText);
            return;
        }

        if (!isValidEmail(data.email)) {
            showAlert('Please enter a valid email address', 'error');
            hideLoading(submitBtn, originalText);
            return;
        }

        try {
            const res = await fetch(`${BASE_URL}/login`, { // 🔧 FIX
                method: "POST",
                headers: { 
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                body: JSON.stringify(data)
            });

            const result = await res.json();
            
            if (!res.ok) throw new Error(result.error);

            localStorage.setItem("token", result.access_token);
            localStorage.setItem("user_id", data.user_id);  // 🔥 ADD THIS
            showAlert('Login successful! Redirecting...', 'success');

            setTimeout(() => {
                window.location.href =
                    result.role === "student"
                        ? "/student-dashboard-page"
                        : "/manager/dashboard";
            }, 800);

        } catch (error) {
            showAlert(error.message || 'Login failed', 'error');
        } finally {
            hideLoading(submitBtn, originalText);
        }
    });

    // FORGOT PASSWORD
    document.querySelector('.forgot')?.addEventListener('click', (e) => {
        e.preventDefault();
        const email = prompt('Please enter your email address:');
        
        if (email && isValidEmail(email)) {
            fetch(`${BASE_URL}/forgot-password`, { // 🔧 FIX
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email: email.toLowerCase() })
            })
            .then(res => res.json())
            .then(result => {
                if (result.message) {
                    showAlert('Password reset link sent!', 'success');
                } else {
                    showAlert(result.error || 'Failed', 'error');
                }
            });
        }
    });

    function isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    function createParticles() {
        const container = document.createElement('div');
        container.className = 'particles';
        document.body.appendChild(container);

        for (let i = 0; i < 30; i++) {
            const p = document.createElement('div');
            p.className = 'particle';
            container.appendChild(p);
        }
    }
});
