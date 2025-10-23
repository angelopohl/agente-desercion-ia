import smtplib
import os
from email.message import EmailMessage
from dotenv import load_dotenv

# Carga las variables (EMAIL_USER, EMAIL_PASS) desde el archivo .env
load_dotenv()

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

def send_email(to_email: str, subject: str, body: str) -> bool:
    """
    Función genérica para conectarse a Gmail y enviar un correo.
    """
    # Verifica que las credenciales se hayan cargado desde .env
    if not EMAIL_USER or not EMAIL_PASS:
        print("Error: Credenciales EMAIL_USER o EMAIL_PASS no están en .env")
        return False

    # Crear el objeto del mensaje
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = f"Agente de IA Tecsup <{EMAIL_USER}>"
    msg['To'] = to_email

    try:
        # Conectarse al servidor SMTP de Gmail
        print(f"Intentando enviar email a: {to_email}...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Iniciar conexión segura
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
        server.quit()
        print(f"Email enviado exitosamente a: {to_email}")
        return True
    except Exception as e:
        print(f"Error al enviar email: {e}")
        return False

def send_teacher_alert(student_name: str, teacher_email: str, diagnostic_reason: str):
    """
    Envía una alerta al profesor/tutor.
    """
    subject = f"Alerta de IA: Riesgo de deserción detectado para {student_name}"
    body = (
        f"Estimado docente,\n\n"
        f"Nuestro agente de IA ha identificado que el estudiante {student_name} presenta un alto riesgo de deserción.\n\n"
        f"**Diagnóstico Principal:** {diagnostic_reason}.\n\n"
        f"Se sugiere contactar al estudiante para una intervención oportuna y ofrecerle apoyo académico.\n\n"
        f"Atentamente,\n"
        f"Agente de Retención Estudiantil Tecsup"
    )
    return send_email(teacher_email, subject, body)

def send_student_support(student_name: str, student_email: str, support_resource: str):
    """
    Envía un correo de apoyo al estudiante.
    """
    subject = f"¡Hola {student_name}! Tenemos nuevos recursos de apoyo para ti"
    body = (
        f"¡Hola {student_name}!\n\n"
        f"Soy tu asistente académico de IA. Para apoyarte en tu éxito este semestre, hemos encontrado algunos recursos que podrían serte muy útiles:\n\n"
        f"**Recurso Recomendado:**\n"
        f"{support_resource}\n\n"
        f"Recuerda que estamos aquí para ayudarte. ¡Mucho éxito!\n\n"
        f"Atentamente,\n"
        f"Tu Asistente Académico IA"
    )
    return send_email(student_email, subject, body)


# --- AÑADIR ESTAS DOS NUEVAS FUNCIONES AL FINAL DEL ARCHIVO ---

def send_teacher_medium_alert(student_name: str, teacher_email: str, risk_prob: float):
    """
    Envía una alerta PREVENTIVA al profesor/tutor para Riesgo Medio.
    """
    subject = f"Aviso de IA: Monitoreo preventivo para {student_name}"
    body = (
        f"Estimado docente,\n\n"
        f"Nuestro agente de IA ha identificado que el estudiante {student_name} presenta un **Riesgo Medio** de deserción (Probabilidad: {risk_prob:.1%}).\n\n"
        f"No se requiere una acción urgente, pero se recomienda un seguimiento preventivo en las próximas semanas para asegurar su progreso.\n\n"
        f"Atentamente,\n"
        f"Agente de Retención Estudiantil Tecsup"
    )
    return send_email(teacher_email, subject, body)

def send_student_medium_support(student_name: str, student_email: str):
    """
    Envía un correo de apoyo "ligero" al estudiante para Riesgo Medio.
    """
    subject = f"¡Hola {student_name}! Recursos de apoyo disponibles"
    body = (
        f"¡Hola {student_name}!\n\n"
        f"Soy tu asistente académico de IA. Queremos asegurarnos de que tengas todo lo necesario para tener éxito.\n\n"
        f"Te recordamos que la universidad ofrece servicios de tutoría y consejería. Puedes encontrar más información aquí:\n"
        f"[Link a Servicios Estudiantiles Generales]\n\n"
        f"¡Sigue adelante! Estamos para apoyarte.\n\n"
        f"Atentamente,\n"
        f"Tu Asistente Académico IA"
    )
    return send_email(student_email, subject, body)