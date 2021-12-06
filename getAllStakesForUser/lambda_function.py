import boto3
import botocore
from boto3.dynamodb.conditions import Key, Attr


def lambda_handler(event, context):
    if 'username' not in event:
        return 'username is required!'
    dynamodb = boto3.resource('dynamodb', region_name='REGION_NAME')
    internal_stakes_table = dynamodb.Table('internalTransactions')
    stakes_response = internal_stakes_table.query(
        IndexName='type-username-index',
        KeyConditionExpression=Key('type').eq('STAKE') & Key('username').eq(event['username'])
    )
    stakes = stakes_response['Items']
    while stakes_response.get('LastEvaluatedKey'):
        stakes_response = internal_stakes_table.query(
            IndexName='type-username-index',
            ExclusiveStartKey=stakes_response.get('LastEvaluatedKey'),
            KeyConditionExpression=Key('type').eq('STAKE') & Key('username').eq(event['username'])
            )
        stakes.extend(stakes_response['Items'])
    return stakes