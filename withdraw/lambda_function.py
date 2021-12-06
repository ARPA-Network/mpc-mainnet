import uuid
import boto3, json, typing
import botocore
from boto3.dynamodb.conditions import Key, Attr

MIN_WITHDRAW_AMOUNT = 2000
FEE = 200

def lambda_handler(event, context):
    if 'username' not in event or 'anticipatedAmount' not in event:
        return 'username, anticipatedAmount are all required!'
    if int(event['anticipatedAmount']) < MIN_WITHDRAW_AMOUNT:
        return 'withdrawl is below minimum required amount!'
    dynamodb = boto3.resource('dynamodb', region_name='REGION_NAME')
    table = dynamodb.Table('accounts')
    response = table.get_item(Key={'username': event['username']})
    if 'Item' not in response:
        return 'account not found!'
    account = response['Item']
    if int(event['anticipatedAmount']) > account['balance']:
        return 'not enough balance!'
        
    external_transactions_table = dynamodb.Table('externalTransactions')
    withdrawls_response = external_transactions_table.query(
        IndexName='direction-username-index',
        KeyConditionExpression=Key('direction').eq(-1) & Key('username').eq(event['username'])
    )
    withdrawls = withdrawls_response['Items']
    while withdrawls_response.get('LastEvaluatedKey'):
        withdrawls_response = external_transactions_table.query(
            IndexName='direction-username-index',
            ExclusiveStartKey=withdrawls_response.get('LastEvaluatedKey'),
            KeyConditionExpression=Key('direction').eq(-1) & Key('username').eq(event['username'])
            )
        withdrawls.extend(withdrawls_response['Items'])
    for withdrawl in withdrawls:
        if withdrawl['isPending']:
            return 'there is already a pending withdrawl!'
            
    new_id = str(uuid.uuid1())
    payload = {
        'id': new_id,
        'username': event['username'],
        'anticipatedAmount': int(event['anticipatedAmount']) - FEE,
        'wechat': 'N/A',
        'telegram': 'N/A',
        'description': 'N/A',
        'direction': -1
        }
    client = boto3.client('lambda')
    payload_json = json.dumps(payload)
    payload_json_bytes = bytes(payload_json, encoding='utf8')
    response = client.invoke(
        FunctionName='mpc-createTransaction',
        InvocationType="Event",
        Payload=payload_json_bytes
    )
    print(payload)
    return payload