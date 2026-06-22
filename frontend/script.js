/**
 * Login Handler Script
 * Connects the login form to the AuthService API class.
 */

async function login() {
    const usernameInput = document.getElementById('usuario');
    const passwordInput = document.getElementById('clave');
    const button = document.querySelector('.btn--primary');
    
    const username = usernameInput.value.trim();
    const password = passwordInput.value;

    if (!username || !password) {
        alert('Por favor ingresa usuario y contraseña');
        return;
    }

    button.disabled = true;
    button.textContent = 'Verificando...';

    try {
        console.log('🔄 Attempting login for user:', username);
        console.log('📡 Backend URL:', 'http://localhost:8000/api/auth/login');
        
        const authService = new AuthService();
        const response = await authService.login({
            username: username,
            password: password
        });

        console.log('✅ Login successful:', response);
        alert('¡Login exitoso! Redirigiendo al dashboard...');
        
        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 1000);

    } catch (error) {
        console.error('❌ Login error:', error);
        console.error('Error message:', error.message);
        console.error('Error stack:', error.stack);
        
        alert(`Error de login: ${error.message}\n\nVerifica:\n1. El backend está corriendo en puerto 8000\n2. Las credenciales son correctas\n3. El usuario existe en MongoDB`);
        
        button.disabled = false;
        button.textContent = 'Ingresar al workspace';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const passwordInput = document.getElementById('clave');
    
    passwordInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            login();
        }
    });

    if (ApiConfig.isAuthenticated()) {
        console.log('User already authenticated, redirecting...');
        window.location.href = 'dashboard.html';
    }
});