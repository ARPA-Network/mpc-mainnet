import boto3
import botocore

def lambda_handler(event, context):
    if 'username' not in event:
        return 'username is required!'
    dynamodb = boto3.resource('dynamodb', region_name='REGION_NAME')
    table = dynamodb.Table('addresses')
    response = table.get_item(Key={'username': event['username']})
    return response['Item'] if 'Item' in response else {}