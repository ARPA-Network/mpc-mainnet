import boto3
import botocore
import time

def lambda_handler(event, context):
    if 'id' not in event or 'actualAmount' not in event or 'transactionHash' not in event:
        return 'id, actualAmount, transactionHash are all required!'
    dynamodb = boto3.resource('dynamodb', region_name='REGION_NAME')
    external_transactions_table = dynamodb.Table('externalTransactions')
    accounts_table = dynamodb.Table('accounts')
    response = external_transactions_table.get_item(Key={'id': event['id']})
    if 'Item' not in response:
        return 'deposit not found!'
    elif not response['Item']['isPending']:
        return 'the deposit has already been processed!'
    elif response['Item']['isApproved']:
        return 'cannot reject an approved deposit!'
    elif response['Item']['isRejected']:
        return 'the deposit is already rejected!'
    elif response['Item']['direction'] != 1:
        return 'the transaction is not a deposit!'
    event['direction'] = response['Item']['direction']
    return event
    