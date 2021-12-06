import boto3
import botocore
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    print(event)
    payload = event['responsePayload']
    nodes = payload['nodes']
    print(nodes)
    dynamodb = boto3.resource('dynamodb', region_name='REGION_NAME')
    table = dynamodb.Table('nodes')
    try:
        for node in nodes:
            response = table.update_item(
                Key={
                    'username': node['username']
                },
                UpdateExpression="set isBusy = :bool",
                ExpressionAttributeValues={
                    ':bool': True,
                    },
                ReturnValues="UPDATED_NEW"
            )
    except ClientError as e:
        raise
    else:
        return payload