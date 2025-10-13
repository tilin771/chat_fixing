import boto3
import json
import logging
import traceback


logger = logging.getLogger()
logger.setLevel(logging.INFO)


bedrock_agent_runtime = boto3.client(service_name="bedrock-agent-runtime")
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table("usuarios_permitidos")


def verificar_usuario(cod_usuario: str) -> bool:
    response = table.get_item(Key={'user_id': cod_usuario})
    return 'Item' in response

def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")
    
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

        # Extraer los valores del nuevo formato
        properties = body.get('requestBody', {}).get('content', {}).get('application/json', {}).get('properties', [])
        
        # Buscar pregunta y prioridad en las propiedades
        input_text = None
        cod_usuario = None

        # Extraer parámetros
        for prop in properties:
            if prop.get('name') == 'pregunta':
                input_text = prop.get('value')
            elif prop.get('name') == 'cod_usuario':
                cod_usuario = prop.get('value')

        logger.info(f"Extracted values - pregunta: {input_text}, cod_usuario: {cod_usuario}")

        if not input_text:
            raise ValueError("'pregunta' field is required and cannot be empty")
        if not cod_usuario:
            raise ValueError("'cod_usuario' field is required and cannot be empty")
        
        prioridad = 9 if verificar_usuario(cod_usuario) else 7

        logger.info(f"Prioridad del usuario {prioridad}")

        # Configuración de la KB
        KB_ID = "D1TTDMUGC6"
        model_arn = "us.amazon.nova-pro-v1:0"

        # Construir el filtro de metadatos
        metadata_filter = {
            "lessThanOrEquals": {
                "key": "Prioridad",
                "value": prioridad
            }
        }

        # Llamada a Bedrock Agent
        response = bedrock_agent_runtime.retrieve_and_generate(
            input={
                'text': input_text
            },
            retrieveAndGenerateConfiguration={
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': KB_ID,
                    'modelArn': model_arn,
                    'retrievalConfiguration': {
                        'vectorSearchConfiguration': {
                            'filter': metadata_filter,
                            'numberOfResults': 10
                        }
                    }
                },
                'type': 'KNOWLEDGE_BASE'
            }
        )

        logger.info(f"Bedrock response: {json.dumps(response)}")

        # Extraer la respuesta y referencias
        output_text = response['output']['text']
        
        # Formatear las referencias
        citations = response.get('citations', [])
        formatted_references = []

        for citation in citations:
            references = citation.get('retrievedReferences', [])
            for ref in references:
                formatted_ref = {
                    'source': ref.get('metadata', {}).get('source', ''),
                    'priority': ref.get('metadata', {}).get('Prioridad', ''),
                    'location': ref.get('location', {}).get('s3Location', {}).get('uri', '')
                }
                formatted_references.append(formatted_ref)

        # Crear el resultado formateado
        result_text = {
            'respuesta': output_text,
            'referencias': formatted_references,
            'metadata': {
                'total_referencias': len(formatted_references)
            }
        }

        # Formato de respuesta requerido
        formatted_response = {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": event.get("actionGroup"),
                "apiPath": event.get("apiPath"),
                "httpMethod": event.get("httpMethod"),
                "httpStatusCode": 200,
                "responseBody": {
                    "application/json": {
                        "body": json.dumps(result_text)
                    }
                },
                "sessionAttributes": event.get("sessionAttributes", {})
            }
        }

        return formatted_response        

    except boto3.exceptions.Boto3Error as e:
        logger.error(f"Boto3 Error: {str(e)}\n{traceback.format_exc()}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Error en el servicio de AWS',
                'details': str(e)
            })
        }
    
    except json.JSONDecodeError as e:
        logger.error(f"JSON Decode Error: {str(e)}\n{traceback.format_exc()}")
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Error al procesar el JSON de entrada',
                'details': str(e)
            })
        }

    except ValueError as e:
        logger.error(f"Value Error: {str(e)}")
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }

    except Exception as e:
        logger.error(f"Error general: {str(e)}\n{traceback.format_exc()}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Error interno del servidor',
                'details': str(e)
            })
        }