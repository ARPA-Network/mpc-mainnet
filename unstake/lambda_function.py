import boto3
import botocore
import time
from datetime import date
import uuid

MIN_UNSTAKE_AMOUNT = 50

def lambda_handler(event, context):
    if 'id' not in event:
        return 'id is required!'
    dynamodb = boto3.resource('dynamodb', region_name='REGION_NAME')
    internal_transactions_table = dynamodb.Table('internalTransactions')
    response = internal_transactions_table.get_item(Key={'id': str(event['id'])})
    existing_transaction = response['Item']
    if existing_transaction['type'] != 'STAKE':
        return 'the transaction is not a stake!'
    if existing_transaction['isPendingWithdrawl']:
        return 'the withdrawl of the stake has already been claimed!'
    if existing_transaction['isWithdrawn']:
        return 'the stake has already been withdrawn!'
    try:
        response = internal_transactions_table.update_item(
            Key={'id': str(event['id'])},
            UpdateExpression="set isPendingWithdrawl = :isPendingWithdrawl, unstakeDateStamp = :unstakeDateStamp",
            ExpressionAttributeValues={
                ':isPendingWithdrawl': True,
                ':unstakeDateStamp': str(date.today())
            },
            ReturnValues="UPDATED_NEW",
            )
    except Exception as e:
        print(e)
        return 1
    return existing_transaction