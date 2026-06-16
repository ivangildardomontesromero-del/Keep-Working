let usuarioActual = "";

// Lógica de Registro / Login simulado
const registroForm = document.getElementById('registroForm');
const authSection = document.getElementById('auth-section');
const mainApp = document.getElementById('main-app');
const usuarioDisplay = document.getElementById('usuario-display');

registroForm.addEventListener('submit', (e) => {
    e.preventDefault();
    usuarioActual = document.getElementById('regUsuario').value;
    
    // Ocultar login, mostrar app principal
    authSection.style.display = 'none';
    mainApp.style.display = 'block';
    usuarioDisplay.textContent = `Atleta: ${usuarioActual}`;
});

// Lógica del Formulario de IA (Múltiples botones)
const planForm = document.getElementById('planForm');
const resultadoDiv = document.getElementById('resultadoPlan');

// Variable para guardar qué botón se presionó
let accionSeleccionada = "";
const botones = document.querySelectorAll('.action-buttons button');
botones.forEach(btn => {
    btn.addEventListener('click', (e) => {
        accionSeleccionada = e.target.value; // Puede ser 'rutina', 'dieta', o 'ambos'
    });
});

planForm.addEventListener('submit', async (e) => {
    e.preventDefault(); 
    
    const edad = document.getElementById('edad').value;
    const estatura = document.getElementById('estatura').value;
    const peso = document.getElementById('peso').value;
    const complexion = document.getElementById('complexion').value;
    const deporte = document.getElementById('deporte').value;

    resultadoDiv.innerHTML = '<p style="color: var(--gold);">Procesando biometría y generando plan con IA...</p>';
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
