import boto3
import botocore
from boto3.dynamodb.conditions import Key, Attr


def lambda_handler(event, context):
    if 'username' not in event:
        return 'username is required!'
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
    return deposits