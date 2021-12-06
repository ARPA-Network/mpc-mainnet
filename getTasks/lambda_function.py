import boto3
import botocore
from boto3.dynamodb.conditions import Key, Attr

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb', region_name='REGION_NAME')
    tasks_table = dynamodb.Table('tasks')
    response = tasks_table.query(
        IndexName='numPlayers-serialNumber-index',
        KeyConditionExpression=Key('numPlayers').eq(3) & Key('serialNumber').between(int(event['from']), int(event['to']))
        )
    if response['Items']:
        tasks = response['Items']
        for task in tasks:
            del task['nodeMap']
            del task['statuses']
            del task['programId']
            task['reward'] = 15
        return tasks
    return []