import boto3
import botocore
import time
from functools import reduce

def lambda_handler(event, context):
    return getLatestCount()
    
def getLatestCount():
    dynamodb = boto3.resource('dynamodb', region_name='REGION_NAME')
    table = dynamodb.Table('universalTrackers')
    response = table.get_item(Key={'trackerType': 'taskCounter'})
    return response['Item']['trackerValue']