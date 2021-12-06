import boto3
import botocore
from boto3.dynamodb.conditions import Key, Attr

def lambda_handler(event, context):
    total_amount = 0
    withdrawn_amount = 0
    try:
        dynamodb = boto3.resource('dynamodb', region_name='REGION_NAME')
        table = dynamodb.Table('rewards')
        response = table.query(
            IndexName='username-index',
            KeyConditionExpression=Key('username').eq(event['username']),
        )
        all_rewards = response['Items']
        while response.get('LastEvaluatedKey'):
            response = table.query(
                IndexName='username-index',
                ExclusiveStartKey=response['LastEvaluatedKey'],
                KeyConditionExpression=Key('username').eq(event['username']),
                )
            all_rewards.extend(response['Items'])
        print(len(all_rewards))
    except:
        raise
    for reward in all_rewards:
        total_amount += int(reward['amount'])
        if reward['isWithdrawn']:
            withdrawn_amount += int(reward['amount'])
    return {'totalAmount': total_amount, 'withdrawnAmount': withdrawn_amount}