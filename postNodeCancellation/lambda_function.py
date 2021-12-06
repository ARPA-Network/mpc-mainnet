import boto3
import botocore
from datetime import date
import time

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb', region_name='REGION_NAME')
    addresses_table = dynamodb.Table('cancellations')
    if 'username' not in event:
        return 1
    event['staking'] = 'N/A'
    event['txHash'] = 'N/A'
    event['date'] = str(date.today())
    event['timestamp'] = str(time.time())
    event['isProcessed'] = False
    try:
        response = addresses_table.put_item(Item=event)
        print(response)
    except Exception as e:
        print(e)
        return 1
    print('new cancellation request is completed')
    return 0