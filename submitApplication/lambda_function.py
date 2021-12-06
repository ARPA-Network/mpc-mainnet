import boto3
import botocore
import time

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb', region_name='REGION_NAME')
    applications_table = dynamodb.Table('applications')
    for key in event:
        if event[key] == '':
            event[key] = 'N/A'
    event['isAdmitted'] = False
    event['hasPaidDeposit'] = False
    event['hasStaked'] = False
    event['timestamp'] = str(time.time())
    try:
        applications_table.put_item(
            Item=event,
            ConditionExpression='attribute_not_exists(username)'
            )
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return 1
    print('insert new application completed')
    return 0
