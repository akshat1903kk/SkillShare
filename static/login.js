const loginForm = document.getElementById('login-form');
        const registerForm = document.getElementById('register-form');
        const switchBtn = document.getElementById('switch-btn');
        const formTitle = document.getElementById('form-title');
        const loginError = document.getElementById('login-error');
        const registerError = document.getElementById('register-error');

        switchBtn.addEventListener('click', () => {
            loginForm.classList.toggle('hidden');
            registerForm.classList.toggle('hidden');
            loginError.textContent = "";
            registerError.textContent = "";

            if (loginForm.classList.contains('hidden')) {
                formTitle.textContent = "Register";
                switchBtn.textContent = "Switch to Login";
            } else {
                formTitle.textContent = "Login";
                switchBtn.textContent = "Switch to Register";
            }
        });

        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            loginError.textContent = "";

            const username = document.getElementById('login-username').value;
            const password = document.getElementById('login-password').value;

            try {
                const response = await fetch('/auth/token', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: new URLSearchParams({ username, password })
                });

                if (response.ok) {
                    const data = await response.json();
                    localStorage.setItem('token', data.access_token);
                    window.location.href = '/dashboard';
                } else {
                    const errorData = await response.json();
                    loginError.textContent = errorData.detail || "Invalid username or password";
                    console.error("Login Error:", errorData);
                }
            } catch (error) {
                loginError.textContent = "Login failed. Try again.";
                console.error("Login Error:", error);
            }
        });

        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            registerError.textContent = "";

            const username = document.getElementById('register-username').value;
            const password = document.getElementById('register-password').value;
            const email = document.getElementById('register-email').value;
            const phone = document.getElementById('register-phone').value;

            const userData = { username, password, email, phone };

            try {
                const response = await fetch('/auth/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(userData)
                });

                if (response.ok) {
                    alert("Registration successful! Please login.");
                    loginForm.classList.remove('hidden');
                    registerForm.classList.add('hidden');
                    formTitle.textContent = "Login";
                    switchBtn.textContent = "Switch to Register";
                    registerForm.reset();
                } else {
                    const errorData = await response.json();
                    registerError.textContent = errorData.detail || "Registration failed. Try again.";
                    console.error("Registration Error:", errorData);
                }
            } catch (error) {
                registerError.textContent = "Error registering. Try again.";
                console.error("Registration Error:", error);
            }
        });