import boto3
import botocore
import time
from datetime import date
import uuid

def lambda_handler(event, context):
    payload = event
    if 'username' not in payload or 'anticipatedAmount' not in payload or 'direction' not in payload or 'id' not in payload:
        return 1
    
    dynamodb = boto3.resource('dynamodb', region_name='REGION_NAME')
    external_transactions_table = dynamodb.Table('externalTransactions')
    
    transaction = {
        'id': payload['id'],
        'username': payload['username'],
        'anticipatedAmount': int(payload['anticipatedAmount']),
        'actualAmount': 0,
        'isPending': True,
        'isApproved': False,
        'isRejected': False,
        'direction': int(payload['direction']),
        'timestamp': str(time.time()),
        'datestamp': str(date.today()),
        'wechat': payload['wechat'],
        'telegram': payload['telegram'],
        'description': payload['description'],
        'transactionHash': 'N/A',
    }
    
    if transaction['direction'] == -1:
        transaction['actualAmount'] = int(payload['anticipatedAmount'])
    try:
        response = external_transactions_table.put_item(
            Item=transaction
        )
    except Exception as e:
        print(e)
    print(transaction)
    return transaction
