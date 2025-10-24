import sys
import os
import streamlit as st
import json
import uuid


from core.supervisor_agent import run_supervisor
from core.ticketing_agente import run_ticketing
from services.query_kb import consultar_kb_streaming
from app.utils.validators import validate_message

st.title("🤖 Chatbot soporte Autoline con IA")

# ----------------------
# Funciones auxiliares
# ----------------------

from core.robot_agent import run_robot  # Asegúrate de tener esta importación

from core.robot_agent import run_robot  # Asegúrate de tener esta importación

def handle_robot(decision):
    """
    Procesa una acción 'invoke_robot' devuelta por el supervisor.
    Extrae el código de usuario y el tipo de tarea del robot, 
    y ejecuta la acción correspondiente.
    """
    user_code = decision.get("userCode", "")
    robot_task = decision.get("robotTask", {})
    task_type = robot_task.get("type", "")


    if not user_code or not task_type:
        show_answer("No se pudo identificar el código de usuario o el tipo de tarea del robot.")
        return

    prompt = f"Quiero ejecutar la acción '{task_type}', mi código de usuario es {user_code}"
    session_id = st.session_state["session_id"]
    # Ejecutar el robot
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        with st.spinner(f"Ejecutando robot..."):
            try:
                for chunk in run_robot(prompt, session_id):
                    full_response += chunk
                    response_placeholder.markdown(full_response)
            except Exception as e:
                response_placeholder.markdown(f"Error al ejecutar el robot: {e}")
                return

    st.session_state["messages"].append({"role": "assistant", "content": full_response})


def generar_contexto_kb(max_ultimos=5):
    """
    Genera un contexto acumulado de los últimos mensajes de usuario
    y asistente para mejorar las consultas a la KB.
    """
    contexto = ""
    ultimos_mensajes = st.session_state["messages"][-max_ultimos:]
    for msg in ultimos_mensajes:
        rol = "Usuario" if msg["role"] == "user" else "Asistente"
        contexto += f"{rol}: {msg['content']}\n"
    return contexto


def inicializar_sesion():
    """Inicializa las variables de sesión de Streamlit"""
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = str(uuid.uuid4())
    if "ultimo_estado" not in st.session_state:
        st.session_state["ultimo_estado"] = ""
    if "modo_ticket" not in st.session_state:
        st.session_state["modo_ticket"] = False
    if "ticket_iniciado" not in st.session_state:
        st.session_state["ticket_iniciado"] = False
    if "modo_robot" not in st.session_state:
        st.session_state["modo_robot"] = False


def show_answer(texto):
    """Muestra una respuesta del asistente y la guarda en el historial"""
    with st.chat_message("assistant"):
        st.markdown(texto)
    st.session_state["messages"].append({"role": "assistant", "content": texto})


def enviar_saludo_inicial():
    """Envía un saludo automático la primera vez que se inicia la sesión"""
    if "ia_inicializada" not in st.session_state:
        st.session_state["ia_inicializada"] = True
        session_id = st.session_state["session_id"]

        saludo = run_supervisor("hola", session_id)
        try:
            saludo_json = json.loads(saludo)
            saludo_texto = saludo_json.get("userResponse", "")
        except json.JSONDecodeError:
            saludo_texto = "¡Hola! Estoy aquí para ayudarte con Autoline. Me podrías decir tu código de usuario"

        st.session_state["messages"].append({"role": "assistant", "content": saludo_texto})

def generar_resumen_contexto():
    """
    Genera un resumen del historial de conversación para pasar a la creación del ticket.
    """
    resumen = "Resumen de la conversación para que lo tengas en cuenta a la hora de redactar el ticket:\n"
    
    for message in st.session_state["messages"]:
        role = "Usuario" if message["role"] == "user" else "Asistente"
        contenido = message["content"]
        resumen += f"{role}: {contenido}\n"
    
    return resumen


def handle_ticket(user_input):
    """Procesa un mensaje cuando estamos en modo ticket"""
    # Solo en la primera llamada al ticket
    if "ticket_iniciado" not in st.session_state or not st.session_state["ticket_iniciado"]:
        st.session_state["ticket_iniciado"] = True

        # Generar resumen de la conversación hasta este punto
        resumen = generar_resumen_contexto()

        # 🌀 Mostrar la respuesta del ticket en streaming
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            with st.spinner("Procesando ticket automáticamente..."):
                for chunk in run_ticketing(resumen, st.session_state["session_id"]):
                    full_response += chunk
                    response_placeholder.markdown(full_response)

        # Guardar en el historial
        st.session_state["messages"].append({"role": "assistant", "content": full_response})
        st.rerun()

    else:
        # Para mensajes posteriores en modo ticket
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            with st.spinner("Actualizando ticket..."):
                for chunk in run_ticketing(user_input, st.session_state["session_id"]):
                    full_response += chunk
                    response_placeholder.markdown(full_response)

        st.session_state["messages"].append({"role": "assistant", "content": full_response})
        st.rerun()        

def manejar_accion(decision, user_input):
    """Procesa la acción devuelta por el supervisor"""
    accion = decision.get("action", "")

    if accion == "query_kb":
        contexto = generar_contexto_kb(max_ultimos=5)  
        consulta_con_contexto = f"{contexto}\nPregunta del usuario: {user_input}"
        full_response = ""
        
        # Abrimos el mensaje del asistente para el streaming
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            with st.spinner("Consultando base de conocimiento..."):
                for partial_response in consultar_kb_streaming(user_input, consulta_con_contexto, prioridad=7):
                    texto = partial_response.strip()
                    
                    if "create" in texto:
                        response_placeholder.empty()
                        break 

                    full_response += partial_response
                    response_placeholder.markdown(full_response)
                else:
                    # Este else se ejecuta SOLO si el bucle terminó normalmente (sin break)
                    full_response += f"\n\n**{decision.get('confirmationMessage', '')}**"
                    response_placeholder.markdown(full_response)
                    st.session_state["messages"].append({"role": "assistant", "content": full_response})
                    return  # Fin normal

        # Si llegamos aquí, fue porque hubo un "break" → se detectó "create"
        st.session_state["modo_ticket"] = True
        handle_ticket(user_input)  # Esto crea su propio st.chat_message, limpio
        return

    elif accion in ("create_ticket", "query_tickets"):
        st.session_state["modo_ticket"] = True
        handle_ticket(user_input)
    
    elif accion == "invoke_robot":
        st.session_state["modo_robot"] = True
        handle_robot(decision)
        
        
    else:
        full_response = decision.get("userResponse", "")
        show_answer(full_response)

    st.session_state["ultimo_estado"] = f"Estado: {decision.get('status', '')}, Paso siguiente: {decision.get('nextStep', '')}"



def procesar_mensaje(user_input):
    """Procesa el input del usuario"""
    session_id = st.session_state["session_id"]

    # Guardar mensaje del usuario
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Validar mensaje
    errores = validate_message(user_input)
    if errores:
        mensaje_errores = "Se encontraron los siguientes errores:\n\n" + "\n".join(f"- {e}" for e in errores)
        show_answer(mensaje_errores)
        return

    # Si estamos en modo ticket
    if st.session_state["modo_ticket"]:
        handle_ticket(user_input)
        return

    # Caso general: pedir decisión al supervisor
    decision = run_supervisor(user_input, session_id)
    try:
        decision = json.loads(decision)
    except json.JSONDecodeError:
        st.error("Error al procesar la respuesta de la IA")
        decision = {}

    manejar_accion(decision, user_input)


# ----------------------
# Código principal
# ----------------------

inicializar_sesion()
enviar_saludo_inicial()

# Mostrar mensajes previos
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input del usuario
user_input = st.chat_input("Escribe tu consulta...")
if user_input:
    procesar_mensaje(user_input)