import boto3
import botocore
from boto3.dynamodb.conditions import Key, Attr
import uuid

dynamodb_resource = boto3.resource('dynamodb', region_name='REGION_NAME')

def lambda_handler(event, context):
    # withdraws_table = dynamodb_resource.Table('withdraws')
    # withdraw = {
    #     'withdrawId': str(uuid.uuid1()),
    #     'txnHash': 'N/A',
    #     'amount': int(event['messageAttributes']['amount']['stringValue']),
    #     'completed': False
    # }
    # try:
    #     response = addresses_table.put_item(Item=withdraw)
    #     print(response)
    print(event)
    print(event['Records'][0]['messageAttributes']['username']['stringValue'])
    print(int(event['Records'][0]['messageAttributes']['amount']['stringValue']))
    return ''