import json
import boto3
import requests
import logging
import re

# Configure logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        # Parsing del body
        if isinstance(event, str):
            body = json.loads(event)
        elif isinstance(event, dict):
            if 'body' in event:
                body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
            else:
                body = event

        logger.info(f"Parsed body: {json.dumps(body)}")

        # Extraer 'cod_usuario' del requestBody anidado
        request_body = body.get('requestBody', {})
        content = request_body.get('content', {})
        json_content = content.get('application/json', {})
        properties = json_content.get('properties', [])

        logger.info(f"Properties: {json.dumps(properties)}")

        cod_usuario = None

        for prop in properties:
            if prop.get("name") == "cod_usuario":
                cod_usuario = prop.get("value")
                break

        if not cod_usuario:
            raise ValueError("No se pudo extraer el cod_usuario del requestBody")
        
        logger.info(cod_usuario)


        token_url = "https://cloud.uipath.com/identity_/connect/token"
        token_data = {
            "grant_type": "client_credentials",
            "client_id": "56e549a0-5898-4260-b498-b3dafd1dd776",
            "client_secret": "",
            "scope": "OR.Execution OR.Jobs"
        }

        token_headers = {"Content-Type": "application/x-www-form-urlencoded"}

        token_response = requests.post(token_url, data=token_data, headers=token_headers)
        token_response.raise_for_status()
        access_token = token_response.json()["access_token"]

        orchestrator_url = (
            "https://cloud.uipath.com/serviciosoperativossa/DefaultTenant/orchestrator_"
            "/odata/Jobs/UiPath.Server.Configuration.OData.StartJobs"
        )

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
            "X-UIPATH-OrganizationUnitId": "2888285",
            "X-UIPATH-TenantName": "DefaultTenant",
            "X-UIPATH-FolderPath": "DEV"
        }

        job_payload = {
            "startInfo": {
                "ReleaseKey": "7606a6b3-d3cf-404b-b1fb-a7f441c3f4f3",
                "Strategy": "JobsCount",
                "JobsCount": 1,
                "InputArguments": json.dumps({
                    "in_str_CodUsuario": str(cod_usuario)
                })
            }
        }

        logger.info(f"Job Payload: {json.dumps(job_payload)}")

        orchestrator_response = requests.post(
            orchestrator_url, headers=headers, json=job_payload
        )
        orchestrator_response.raise_for_status()
        orchestrator_data = orchestrator_response.json()

        job_key = orchestrator_data["value"][0]["Key"]
        state = orchestrator_data["value"][0]["State"]

        result_text = (
            f"✅ Robot ejecutado en UiPath.\n"
            f"- Job Key: {job_key}\n"
            f"- Estado inicial: {state}"
        )

        logger.info(result_text)

        response = {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": body["actionGroup"],
                "apiPath": body["apiPath"],
                "httpMethod": body["httpMethod"],
                "httpStatusCode": 200,
                "responseBody": {
                    "application/json": {
                        "body": json.dumps(result_text)
                    }
                },
                "sessionAttributes": body["sessionAttributes"]
            }
        }

        return response

    except Exception as e:
        logger.error(f"Error en lambda_handler: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
