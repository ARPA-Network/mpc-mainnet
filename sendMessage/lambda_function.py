import json
import boto3
import os

dynamodb = boto3.client('dynamodb', region_name='REGION_NAME')

def handle(event, context):
    connectionId = event['requestContext']['connectionId']

    # Insert the connectionId of the connected device to the database
    # dynamodb.put_item(TableName='connections', Item={'connectionId': {'S': connectionId}})

    return (event, context)