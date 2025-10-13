import json
import requests
from datetime import datetime
from base64 import b64encode
import logging

# Configurar logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Configuración de autenticación básica
USERNAME = "apirest"
PASSWORD = ""
CREDENTIALS = f"{USERNAME}:{PASSWORD}"
ENCODED_CREDENTIALS = b64encode(CREDENTIALS.encode()).decode()
HEADERS = {
    "Authorization": f"Basic {ENCODED_CREDENTIALS}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def create_response(event, status_code, message):
    return {
        "messageVersion": "1.0",
        "response": {
            "actionGroup": event.get("actionGroup"),
            "apiPath": event.get("apiPath"),
            "httpMethod": event.get("httpMethod"),
            "httpStatusCode": status_code,
            "responseBody": {
                "application/json": {
                    "body": json.dumps(message)
                }
            },
            "sessionAttributes": event.get("sessionAttributes", {})
        }
    }

def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")

    path = event.get("apiPath", "")
    method = event.get("httpMethod", "")

    try:
        if path == "/createTicket" and method == "POST":
            logger.info("CREANDO TICKET....")
            return handle_create_ticket(event)
        elif path == "/requests" and method == "GET":
            logger.info("CONSULTANDO TICKET....")
            return handle_get_tickets(event)
        elif path == "/requests/comment" and method == "GET":
            logger.info("CONSULTANDO COMENTARIOS....")
            return handle_get_ticket_comments(event)
        else:
            return create_response(event, 400, f"Ruta o método no soportado: {method} {path}")
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        return create_response(event, 500, f"Error interno del servidor: {str(e)}")


def handle_create_ticket(event):
    now = datetime.now().strftime("%d/%m/%Y %H:%M")

    try:
        properties = event.get('requestBody', {}).get('content', {}).get('application/json', {}).get('properties', [])

        requestor_mail = None
        description = None
        title = None

        for prop in properties:
            name = prop.get('name', '').strip() 
            if name.lower() == 'requestor_mail': 
                requestor_mail = prop.get('value')
            elif name.lower() == 'description':
                description = prop.get('value')
            elif name.lower() == 'title':
                title = prop.get('value')

        logger.info(f"Extracted values - Requestor_mail: {requestor_mail}, Description: {description}, Title: {title}")

        if not requestor_mail or not description:
            return create_response(event, 400, "Los campos Requestor_Mail y Description son obligatorios.")

        ticket_data = {
            "requests": [
                {
                    "Catalog_Code": "INC395",
                    "Title": title,
                    "Requestor_Mail": "gconchello@servosa.com",
                    "Recipient_Mail": "ppie@servosa.com",
                    "Urgency_ID": 1,
                    "Severity_ID": 30,
                    "Origin": "API",
                    "Description": description,
                    "Submit_Date": now
                }
            ]
        }

        logger.info(f"Body enviado para crear ticket: {ticket_data}" )

        url = "https://easydeskagente.quadis.es/api/v1/50005/requests"
        response = requests.post(url, headers=HEADERS, json=ticket_data)
        response.raise_for_status()

        if response.status_code == 201:
            ticket_href = response.json().get("HREF", "No disponible")
            result_text = f"Ticket creado correctamente en EasyVista.\n📄 [Ver ticket]({ticket_href})"
            logger.info(result_text)
            return create_response(event, 200, result_text)
        else:
            return create_response(event, response.status_code, f"Ticket no creado. Respuesta: {response.text}")

    except requests.exceptions.RequestException as e:
        logger.error(f"Error al crear ticket: {str(e)}")
        return create_response(event, 500, f"Error al crear ticket: {str(e)}")

def handle_get_tickets(event):
    try:
        employee_id = None
        for param in event.get("parameters", []):
            if param.get("name") == "employee_id":
                employee_id = param.get("value")
                break

      

        if not employee_id:
            return create_response(event, 400, "El parámetro 'employee_id' es obligatorio para consultar tickets.")

        
        search = f'requestor.employee_id:"{employee_id}"'
        url = f"https://easydeskagente.quadis.es/api/v1/50005/requests?search={search}"

        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()

        tickets = response.json()

        simplified = []
        for record in tickets.get("records", []):
            simplified.append({
                "RFC_NUMBER": record.get("RFC_NUMBER"),
                "SUBMIT_DATE": record.get("SUBMIT_DATE_UT"),
                "STATUS": record.get("STATUS", {}).get("STATUS_SP")
            })

        return create_response(event, 200, simplified)

    except requests.exceptions.RequestException as e:
        logger.error(f"Error al consultar tickets: {str(e)}")
        return create_response(event, 500, f"Error al consultar tickets: {str(e)}")

def handle_get_ticket_comments(event):
    try:
        ticket_id = None
        for param in event.get("parameters", []):
            if param.get("name") == "ticket_id":
                ticket_id = param.get("value")
                break

        if not ticket_id:
            return create_response(event, 400, "El parámetro 'ticket_id' es obligatorio para consultar comentarios.")

        logger.info(f"Consultando comentarios del ticket: {ticket_id}")

        url = f"https://easydeskagente.quadis.es/api/v1/50005/requests/{ticket_id}/comment"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()

        comment = response.json()

        simplified = {
            "COMMENT": comment.get("COMMENT"),
            "LINK": comment.get("HREF"),
            "TICKET": comment.get("PARENT_HREF")
        }

        return create_response(event, 200, simplified)

    except requests.exceptions.RequestException as e:
        logger.error(f"Error al consultar comentarios: {str(e)}")
        return create_response(event, 500, f"Error al consultar comentarios: {str(e)}")
