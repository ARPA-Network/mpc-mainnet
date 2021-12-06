import uuid
import boto3, json, typing
import botocore
from boto3.dynamodb.conditions import Key, Attr

MIN_DEPOSIT_AMOUNT = 50000
BUCKET_NAME = 'deposit-screenshots'

def lambda_handler(event, context):
    if 'username' not in event or 'anticipatedAmount' not in event or "imageType" not in event:
        return 'username, anticipatedAmount, imageType are all required!'
    if int(event['anticipatedAmount']) < MIN_DEPOSIT_AMOUNT:
        return 'deposit is below minimum required amount!'
    
    dynamodb = boto3.resource('dynamodb', region_name='REGION_NAME')
    external_transactions_table = dynamodb.Table('externalTransactions')
    deposits_response = external_transactions_table.query(
        IndexName='direction-username-index',
        KeyConditionExpression=Key('direction').eq(1) & Key('username').eq(event['username'])
    )
    deposits = deposits_response['Items']
    while deposits_response.get('LastEvaluatedKey'):
        deposits_response = external_transactions_table.query(
            IndexName='direction-username-index',
            ExclusiveStartKey=deposits_response.get('LastEvaluatedKey'),
            KeyConditionExpression=Key('direction').eq(1) & Key('username').eq(event['username'])
            )
        deposits.extend(deposits_response['Items'])
    for deposit in deposits:
        if deposit['isPending']:
            return 'there is already a pending deposit!'
        
    new_id = str(uuid.uuid1())
    s3 = boto3.client('s3')
    presigned_url = s3.generate_presigned_url(
        ClientMethod='put_object',
        Params={
            'Bucket': BUCKET_NAME,
            'Key': new_id,
            'ContentType': event["imageType"]
        }
    )
    payload = {
        'id': new_id,
        'username': event['username'],
        'anticipatedAmount': int(event['anticipatedAmount']),
        'wechat': event['wechat'] if event['wechat'] != '' or 'wechat' not in event else 'N/A',
        'telegram': event['telegram'] if event['telegram'] != '' or 'telegram' not in event else 'N/A',
        'description': event['description'] if event['description'] != '' or 'description' not in event else 'N/A',
        'direction': 1,
        'uploadUrl': presigned_url
        }
    client = boto3.client('lambda')
    payload_json = json.dumps(payload)
    payload_json_bytes = bytes(payload_json, encoding='utf8')
    response = client.invoke(
        FunctionName='createTransaction',
        InvocationType="RequestResponse",
        Payload=payload_json_bytes
    )
    print(response)
    return payload
    