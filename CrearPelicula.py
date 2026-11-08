import boto3
import uuid
import os
import json
import traceback
from decimal import Decimal


def log(tipo, log_datos):
    # Formato json de log estándar: {"tipo": "INFO" | "ERROR", "log_datos": {...}}
    print(json.dumps({
        'tipo': tipo,
        'log_datos': log_datos
    }, default=str))


def lambda_handler(event, context):
    try:
        # Entrada (json)
        log("INFO", {
            'mensaje': 'Evento recibido',
            'event': event
        })
        tenant_id = event['body']['tenant_id']
        pelicula_datos = event['body']['pelicula_datos']
        nombre_tabla = os.environ["TABLE_NAME"]

        # Proceso
        uuidv4 = str(uuid.uuid4())
        pelicula = {
            'tenant_id': tenant_id,
            'uuid': uuidv4,
            'pelicula_datos': pelicula_datos
        }
        # DynamoDB no acepta float: se convierten a Decimal solo para guardar
        item = json.loads(json.dumps(pelicula), parse_float=Decimal)
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(nombre_tabla)
        response = table.put_item(Item=item)

        # Salida (json)
        log("INFO", {
            'mensaje': 'Pelicula creada',
            'tabla': nombre_tabla,
            'pelicula': pelicula
        })
        return {
            'statusCode': 200,
            'pelicula': pelicula,
            'response': response
        }

    except KeyError as e:
        # Faltan campos en la entrada (tenant_id, pelicula_datos, TABLE_NAME)
        log("ERROR", {
            'mensaje': 'Falta el campo requerido: ' + str(e),
            'error_tipo': 'KeyError',
            'event': event,
            'traceback': traceback.format_exc()
        })
        return {
            'statusCode': 400,
            'error': 'Falta el campo requerido: ' + str(e)
        }

    except Exception as e:
        # Cualquier otro error (DynamoDB, permisos, datos inválidos, etc.)
        log("ERROR", {
            'mensaje': str(e),
            'error_tipo': type(e).__name__,
            'event': event,
            'traceback': traceback.format_exc()
        })
        return {
            'statusCode': 500,
            'error': str(e)
        }
