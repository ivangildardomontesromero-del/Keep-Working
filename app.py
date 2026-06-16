from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

# --- CONFIGURACIÓN DEL BOT DE TELEGRAM ---
TELEGRAM_BOT_TOKEN = '8739775137:AAHQyQji1XaMNNJTc1q_Yr9zGX4WWyJYwlc'
TELEGRAM_CHAT_ID = '6736791252'  # Integrado exitosamente

def enviar_mensaje_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error al enviar Telegram: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generar_plan', methods=['POST'])
def generar_plan():
    datos = request.json
    
    # Recolección de datos
    edad = int(datos.get('edad', 20))
    peso = float(datos.get('peso', 70))
    estatura = float(datos.get('estatura', 170))
    complexion = datos.get('complexion', 'Atlética')
    deporte = datos.get('deporte', 'Running')
    accion = datos.get('accion', 'ambos') # rutina, dieta, o ambos
    usuario = datos.get('usuario', 'Atleta')
    
    # --- CÁLCULOS FÍSICOS DE LA IA ---
    estatura_m = estatura / 100
    imc = peso / (estatura_m ** 2)
    
    # Lógica Nutricional
    calorias_base = 10 * peso + 6.25 * estatura - 5 * edad + 5
    if imc < 18.5:
        objetivo_dieta = "Superávit calórico (Aumento de masa muscular)"
        calorias_meta = calorias_base * 1.5 + 400
        macros = "Proteína: Alta | Carbohidratos: Muy Altos | Grasas: Moderadas"
    elif imc > 25:
        objetivo_dieta = "Déficit calórico (Pérdida de grasa, preservación muscular)"
        calorias_meta = calorias_base * 1.5 - 500
        macros = "Proteína: Muy Alta | Carbohidratos: Moderados a Bajos | Grasas: Saludables"
    else:
        objetivo_dieta = "Mantenimiento y recomposición"
        calorias_meta = calorias_base * 1.5
        macros = "Proteína: Alta | Carbohidratos: Altos (en torno al entreno) | Grasas: Moderadas"

    # Lógica Deportiva (Entrenamiento)
    rutinas_por_deporte = {
        "Fútbol": "Enfoque en agilidad, sprints cortos (HIIT), cambios de dirección y fuerza explosiva en tren inferior.",
        "Béisbol": "Enfoque en potencia rotacional del core, fuerza de hombros/brazos y arranques de velocidad explosiva.",
        "Básquetbol": "Enfoque en pliometría (saltos verticales), resistencia anaeróbica láctica y agilidad lateral.",
        "Running": "Enfoque en resistencia aeróbica (LISS), umbral de lactato, y fuerza preventiva en rodillas y tobillos.",
        "Gimnasia": "Enfoque en flexibilidad activa, fuerza isométrica extrema (anillas/barras) y control estricto del core."
    }
    
    enfoque_entreno = rutinas_por_deporte.get(deporte, "Acondicionamiento general")

    # --- CONSTRUCCIÓN DEL RESULTADO ---
    html_resultado = f"<div class='resultado-header'><h3>Resultados para {usuario}</h3>"
    html_resultado += f"<p><strong>Perfil:</strong> {edad} años | {peso}kg | {estatura}cm | Complexión: {complexion}</p>"
    html_resultado += f"<p><strong>Índice de Masa Corporal (IMC):</strong> {imc:.1f}</p></div>"
    
    if accion in ['rutina', 'ambos']:
        html_resultado += f"<div class='modulo-resultado'><h4>⚙️ Plan de Entrenamiento - {deporte}</h4>"
        html_resultado += f"<p><strong>Foco Biomecánico:</strong> {enfoque_entreno}</p>"
        html_resultado += f"<ul><li><strong>Fase 1:</strong> Movilidad articular y calentamiento específico para {deporte}.</li>"
        html_resultado += f"<li><strong>Fase 2 (Principal):</strong> Desarrollo de {enfoque_entreno.lower()}</li>"
        html_resultado += f"<li><strong>Fase 3:</strong> Fuerza complementaria adaptada a complexión {complexion.lower()}.</li></ul></div>"

    if accion in ['dieta', 'ambos']:
        html_resultado += f"<div class='modulo-resultado'><h4>🍏 Plan Nutricional</h4>"
        html_resultado += f"<p><strong>Objetivo:</strong> {objetivo_dieta}</p>"
        html_resultado += f"<p><strong>Calorías Diarias Estimadas:</strong> {int(calorias_meta)} kcal</p>"
        html_resultado += f"<p><strong>Distribución:</strong> {macros}</p>"
        html_resultado += f"<ul><li><strong>Pre-entreno:</strong> Carbohidratos de rápida absorción para optimizar energía en {deporte}.</li>"
        html_resultado += f"<li><strong>Post-entreno:</strong> Proteína magra para recuperación del tejido muscular.</li></ul></div>"

    # Notificación Telegram
    mensaje_bot = f"🥇 <b>Nuevo plan generado por {usuario}</b>\nDeporte: {deporte}\nAcción: {accion.capitalize()}\nIMC: {imc:.1f}"
    enviar_mensaje_telegram(mensaje_bot)
    
    return jsonify({"plan_html": html_resultado})

@app.route('/ping')
def ping():
    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
