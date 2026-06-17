import threading
import time
from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

# --- CONFIGURACIÓN DEL BOT DE TELEGRAM ---
TELEGRAM_BOT_TOKEN = '8739775137:AAHQyQji1XaMNNJTc1q_Yr9zGX4WWyJYwlc'
TELEGRAM_CHAT_ID = '6736791252'

# Base de datos temporal en memoria para los recordatorios diarios
planes_activos = {}

def enviar_mensaje_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error al enviar Telegram: {e}")

# --- MOTOR DE RECORDATORIOS DIARIOS ESPECÍFICOS ---
def motor_recordatorios():
    while True:
        time.sleep(86400)  # Espera 24 horas exactas
        
        # Revisa si hay un plan activo para enviar el recordatorio de hoy
        if TELEGRAM_CHAT_ID in planes_activos:
            plan = planes_activos[TELEGRAM_CHAT_ID]
            dia_actual = plan['dia_actual']
            
            if dia_actual <= 28:
                rutina_hoy = plan['rutina_mensual'].get(dia_actual, "Día de recuperación activa. Camina 30 mins y estira.")
                mensaje_recordatorio = (
                    f"🔔 <b>¡Recordatorio EliteTraining! - Día {dia_actual}/28</b>\n\n"
                    f"Hola {plan['usuario']}, ¡es hora de entrenar!\n\n"
                    f"<b>Tu rutina de hoy:</b>\n{rutina_hoy}\n\n"
                    "¡Mucha fuerza y disciplina! 💪"
                )
                enviar_mensaje_telegram(mensaje_recordatorio)
                plan['dia_actual'] += 1  # Avanza al siguiente día
            else:
                enviar_mensaje_telegram("🏆 <b>¡Felicidades!</b> Has completado tus 4 semanas de entrenamiento. Ve a la plataforma a generar tu nuevo plan mensual.")
                del planes_activos[TELEGRAM_CHAT_ID] # Borra el plan terminado

hilo_cronometro = threading.Thread(target=motor_recordatorios, daemon=True)
hilo_cronometro.start()

# --- RUTAS DE LA APLICACIÓN WEB ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generar_plan', methods=['POST'])
def generar_plan():
    datos = request.json
    
    edad = int(datos.get('edad', 20))
    peso = float(datos.get('peso', 70))
    estatura = float(datos.get('estatura', 170))
    complexion = datos.get('complexion', 'Atlética')
    deporte = datos.get('deporte', 'Running')
    accion = datos.get('accion', 'ambos')
    usuario = datos.get('usuario', 'Atleta')
    
    # 1. GENERACIÓN DE DIETA ESPECÍFICA
    imc = peso / ((estatura / 100) ** 2)
    calorias = int(10 * peso + 6.25 * estatura - 5 * edad + 5)
    
    if imc < 18.5:
        dieta = f"<b>Superávit ({calorias + 400} kcal)</b><br>Desayuno: 4 huevos, avena con plátano y leche.<br>Comida: 200g pechuga, 2 tazas de arroz, aguacate.<br>Cena: Atún, pasta y aceite de oliva."
    elif imc > 25:
        dieta = f"<b>Déficit ({calorias - 500} kcal)</b><br>Desayuno: 3 claras de huevo, espinacas, té verde.<br>Comida: 150g pescado blanco, ensalada verde abundante.<br>Cena: Pechuga asada, brócoli hervido."
    else:
        dieta = f"<b>Mantenimiento ({calorias} kcal)</b><br>Desayuno: Omelette de 2 huevos, 1 pan integral.<br>Comida: 150g pollo, 1 taza de quinoa, vegetales.<br>Cena: Salmón, ensalada y papa al horno."

    # 2. GENERACIÓN DE RUTINA DE 28 DÍAS (4 SEMANAS)
    banco_ejercicios = {
        "Fútbol": ["Calentamiento articular", "Sprints cortos 10x20m", "Sentadilla con salto 4x12", "Dominio de balón y pases pared 15 min", "Plancha isométrica 4x45 seg"],
        "Béisbol": ["Rotaciones de torso con banda", "Lanzamientos contra red 4x15", "Desplantes laterales 4x10", "Sprints de base a base (30m)", "Remo con mancuerna 4x12"],
        "Básquetbol": ["Saltos al cajón (Pliometría) 4x8", "Tiros libres bajo fatiga (50 tiros)", "Desplazamiento defensivo lateral 5x1 min", "Flexiones explosivas 4x10", "Trabajo de pantorrillas 4x20"],
        "Running": ["Carrera suave (Zona 2) 45 min", "Series en pista: 8x400m al 80%", "Fortalecimiento: Sentadilla búlgara 4x10", "Fartlek (Cambios de ritmo) 30 min", "Tirada larga dominical + estiramiento"],
        "Gimnasia": ["Estiramiento dinámico avanzado 20 min", "Parada de manos asistida 5x30 seg", "Dominadas estrictas 4x8", "Core en anillas o barra 4x10", "Flexibilidad de spagat 10 min"]
    }
    
    ejercicios_deporte = banco_ejercicios.get(deporte, ["Acondicionamiento general", "Cardio 30 min", "Fuerza básica"])
    rutina_mensual = {}
    
    for dia in range(1, 29):
        if dia % 7 in [1, 3, 5, 6]: 
            rutina_mensual[dia] = "\n- ".join([""] + ejercicios_deporte) + f"\n- Adaptado para complexión {complexion}"
        else:
            rutina_mensual[dia] = "Descanso activo: Caminata ligera de 30 mins, movilidad articular y estiramientos profundos."

    # 3. GUARDAR EL PLAN EN EL MOTOR DE RECORDATORIOS
    planes_activos[TELEGRAM_CHAT_ID] = {
        'usuario': usuario,
        'deporte': deporte,
        'dia_actual': 1,
        'rutina_mensual': rutina_mensual
    }

    # 4. CONSTRUCCIÓN DEL HTML PARA LA PÁGINA
    html_resultado = f"<div class='resultado-header'><h3>Plan Mensual para {usuario}</h3>"
    html_resultado += f"<p><strong>Perfil:</strong> {edad} años | {peso}kg | {estatura}cm | IMC: {imc:.1f}</p></div>"
    
    if accion in ['rutina', 'ambos']:
        html_resultado += f"<div class='modulo-resultado'><h4>⚙️ Rutina - {deporte} (Semanas 1 a 4)</h4>"
        html_resultado += "<p>El bot te enviará diariamente qué ejercicios tocan. Aquí tienes tu estructura semanal:</p>"
        html_resultado += f"<ul><li><strong>Días de carga:</strong><br>- { '<br>- '.join(ejercicios_deporte) }</li>"
        html_resultado += f"<li><strong>Días de recuperación:</strong><br>- Movilidad y estiramientos.</li></ul></div>"

    if accion in ['dieta', 'ambos']:
        html_resultado += f"<div class='modulo-resultado'><h4>🍏 Plan Nutricional Base</h4>"
        html_resultado += f"<p>{dieta}</p></div>"

    html_resultado += "<p style='color:var(--gold); font-weight:bold;'>✅ Tu plan de 28 días está guardado. Revisa tu Telegram, el cronómetro ha comenzado.</p>"

    # Notificación inmediata
    mensaje_bot = f"🥇 <b>¡Plan Mensual Creado!</b>\nHola {usuario}, tu rutina de 28 días de {deporte} está lista. Te enviaré tus ejercicios diariamente por aquí."
    enviar_mensaje_telegram(mensaje_bot)
    
    return jsonify({"plan_html": html_resultado})

@app.route('/ping')
def ping():
    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
