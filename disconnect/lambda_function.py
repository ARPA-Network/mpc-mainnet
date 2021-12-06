import json
import time
import boto3
import logging

logger = logging.getLogger("handler_logger")
logger.setLevel(logging.DEBUG)

def lambda_handler(event, context):
    connection_id = event['requestContext']['connectionId']
    if not connection_id:
        logger.error("Failed: connectionId value not set.")
        return _get_response(500, "connectionId value not set.")
    try:
        dynamodb = boto3.resource('dynamodb', region_name='REGION_NAME')
        table = dynamodb.Table('connections')
        table.delete_item(Key={'connectionId': connection_id})
    except:
        raise
    return _get_response(200, "Disconnected successfully.")

def _get_response(status_code, body):
    if not isinstance(body, str):
        body = json.dumps(body)
    return {"statusCode": status_code, "body": body}