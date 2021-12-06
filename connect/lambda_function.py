import json
import time
from urllib import request
from jose import jwk, jwt
import boto3

key = 'KEY'

def lambda_handler(event, context):
    jwks_url = 'https://url.token/jwks.json'
    audience = 'AUDIENCE_KEY'
    issuer = 'https://url.issuer/key'
    parameters = event['queryStringParameters']
    context = event['requestContext']
    connection_id = ''
    streamer_key = ''
    token_string = ''
    
    if 'connectionId' not in context:
        return _get_response(500, "connectionId value not set.")
    if 'token' not in parameters and 'key' not in parameters:
        return _get_response(400, "token or key query parameter not provided.")
    if 'token' in parameters and 'key' in parameters:
        return _get_response(400, "token and key query parameter are both provided, streamers only need key, viewers only need token.")
        
    if 'token' in parameters:
        token_string = parameters['token']
    if 'key' in parameters:
        streamer_key = parameters['key']
    if 'connectionId' in context:
        connection_id = context['connectionId']
    
    try:
        if token_string:
            print("viewer: {} is connecting...".format(connection_id))
            jwks = request.urlopen(jwks_url)
            payload = jwt.decode(token_string, jwks.read(), algorithms=['RS256'], audience=audience, issuer=issuer)
            print(payload['username'])
            dynamodb = boto3.resource('dynamodb', region_name='REGION_NAME')
            table = dynamodb.Table('connections')
            table.put_item(
                Item={
                    'connectionId': connection_id, 
                    'username': payload['username']
                    }
                )
        elif streamer_key and streamer_key == key:
            print("streamer: {} is connecting...".format(connection_id))
        else:
            return _get_response(400, "invalid token or key.")
    except:
        raise
    return _get_response(200, "Connected successfully.")
    
def _get_response(status_code, body):
    if not isinstance(body, str):
        body = json.dumps(body)
    return {"statusCode": status_code, "body": body}