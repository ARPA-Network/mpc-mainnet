import boto3
import botocore
import time

def lambda_handler(event, context):
    event = event['responsePayload']
    print(event)
    if 'id' not in event or 'actualAmount' not in event:
        return 'id, actualAmount are all required!'
    dynamodb = boto3.resource('dynamodb', region_name='REGION_NAME')
    external_transactions_table = dynamodb.Table('externalTransactions')
    accounts_table = dynamodb.Table('accounts')
    response = external_transactions_table.get_item(Key={'id': event['id']})
    if 'Item' not in response:
        return 'withdrawl not found!'
    elif not response['Item']['isPending']:
        return 'the withdrawl has already been processed!'
    elif response['Item']['isApproved']:
        return 'cannot reject an approved withdrawl!'
    elif response['Item']['isRejected']:
        return 'the withdrawl is already rejected!'
    elif response['Item']['direction'] != -1:
        return 'the transaction is not a withdrawl!'
    event['direction'] = response['Item']['direction']
    return event