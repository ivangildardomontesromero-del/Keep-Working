let usuarioActual = "";

// Elementos de la interfaz
const registroForm = document.getElementById('registroForm');
const authSection = document.getElementById('auth-section');
const mainApp = document.getElementById('main-app');
const usuarioDisplay = document.getElementById('usuario-display');
const btnLogout = document.getElementById('btnLogout');

// --- SISTEMA DE SESIÓN GUARDADA (PERSISTENCIA) ---
document.addEventListener("DOMContentLoaded", () => {
    // Revisar si ya hay un usuario guardado en la memoria del navegador
    const usuarioGuardado = localStorage.getItem("usuario_elite");
    
    if (usuarioGuardado) {
        // Si existe, saltar la pantalla de registro
        usuarioActual = usuarioGuardado;
        authSection.style.display = 'none';
        mainApp.style.display = 'block';
        usuarioDisplay.textContent = `Atleta: ${usuarioActual}`;
    }
});

// Lógica de Inicio de Sesión
registroForm.addEventListener('submit', (e) => {
    e.preventDefault();
    usuarioActual = document.getElementById('regUsuario').value;
    
    // Guardar en la memoria del navegador
    localStorage.setItem("usuario_elite", usuarioActual);
    
    // Mostrar aplicación
    authSection.style.display = 'none';
    mainApp.style.display = 'block';
    usuarioDisplay.textContent = `Atleta: ${usuarioActual}`;
});

// Lógica de Cerrar Sesión
btnLogout.addEventListener('click', () => {
    // Borrar la memoria
    localStorage.removeItem("usuario_elite");
    // Recargar la página para volver al login
    window.location.reload();
});

// --- LÓGICA DE LA IA DEPORTIVA ---
const planForm = document.getElementById('planForm');
const resultadoDiv = document.getElementById('resultadoPlan');

let accionSeleccionada = "";
const botones = document.querySelectorAll('.action-buttons button');
botones.forEach(btn => {
    btn.addEventListener('click', (e) => {
        accionSeleccionada = e.target.value;
    });
});

planForm.addEventListener('submit', async (e) => {
    e.preventDefault(); 
    
    const edad = document.getElementById('edad').value;
    const estatura = document.getElementById('estatura').value;
    const peso = document.getElementById('peso').value;
    const complexion = document.getElementById('complexion').value;
    const deporte = document.getElementById('deporte').value;

    resultadoDiv.innerHTML = '<p style="color: var(--gold);">Calculando ciclo de 28 días...</p>';
    resultadoDiv.style.display = 'block';

    try {
        const response = await fetch('/generar_plan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                edad, estatura, peso, complexion, deporte, 
                accion: accionSeleccionada, 
                usuario: usuarioActual 
            })
        });

        const data = await response.json();
        resultadoDiv.innerHTML = data.plan_html;
        resultadoDiv.scrollIntoView({ behavior: 'smooth' });

    } catch (error) {
        console.error('Error:', error);
        resultadoDiv.innerHTML = '<p style="color:red;">Error de conexión con el servidor.</p>';
    }
});
