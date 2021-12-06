import boto3
import botocore
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    payload = event['responsePayload']
    dynamodb = boto3.resource('dynamodb', region_name='REGION_NAME')
    table = dynamodb.Table('nodes')
    try:
        response = table.update_item(
            Key={
                'username': payload['username']
            },
            UpdateExpression="set isBusy = :bool",
            ExpressionAttributeValues={
                ':bool': False,
                },
            ReturnValues="UPDATED_NEW"
        )
    except Exception as e:
        print(e)
        raise
    else:
        return payload