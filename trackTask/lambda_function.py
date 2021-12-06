import boto3
import botocore
import time
from functools import reduce

dynamodb = boto3.resource('dynamodb', region_name='REGION_NAME')
def lambda_handler(event, context):
    old_count = getLatestCount()
    new_count = old_count + 1
    tasks_table = dynamodb.Table('tasks')
    payload = event['responsePayload']
    node_map = reduce((lambda x, y: {**x, **y}), ({node['username']:node['playerId']} for node in payload['nodes']))
    print(node_map)
    new_task = {
        'taskId': payload['taskId'],
        'programId': payload['programId'],
        'numPlayers': payload['numNodes'],
        'statuses': [],
        'nodeMap': node_map,
        'timestamp': str(time.time()),
        'serialNumber': new_count,
        }
    try:
        response = tasks_table.put_item(
            Item=new_task,
            ConditionExpression='attribute_not_exists(taskId)'
            )
        updateCounter(new_count)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return 1
        else:
            raise
    return 0
    
def getLatestCount():
    table = dynamodb.Table('universalTrackers')
    response = table.get_item(Key={'trackerType': 'taskCounter'})
    return response['Item']['trackerValue']
    
def updateCounter(value):
    table = dynamodb.Table('universalTrackers')
    response = table.update_item(
        Key={'trackerType': 'taskCounter'},
        UpdateExpression="set trackerValue = :value",
        ExpressionAttributeValues={':value': value},
        ReturnValues="UPDATED_NEW",
    )
    return response