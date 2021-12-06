import boto3
import botocore
import random

appication_amount = 50000
lower_bound = 1000
upper_bound = 9000

def lambda_handler(event, context):
    new_amount = random.randint(lower_bound, upper_bound)
    while new_amount in get_existing_amounts():
        new_amount = random.randint(lower_bound, upper_bound)
    dynamodb = boto3.resource('dynamodb', region_name='REGION_NAME')
    identity_amounts_table = dynamodb.Table('identityAmounts')
    try:
        identity_amounts_table.put_item(
            Item={
                'username': event['username'],
                'amount': new_amount
                },
            ConditionExpression='attribute_not_exists(username)'
            )
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            response = identity_amounts_table.get_item(Key={'username': event['username']})
            return int(appication_amount + response['Item']['amount']) if 'Item' in response else 0
    return int(appication_amount + new_amount)
    
def get_existing_amounts():
    dynamodb = boto3.client('dynamodb', region_name='REGION_NAME')
    paginator = dynamodb.get_paginator('scan')
    all_amounts = []
    for page in paginator.paginate(TableName='identityAmounts'):
        amounts = page['Items']
        all_amounts.extend([amount['amount']['N'] for amount in amounts])
    return all_amounts