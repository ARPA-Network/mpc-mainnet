import boto3
import botocore
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb', region_name='REGION_NAME')
table = dynamodb.Table('tasks')

def lambda_handler(event, context):
    # backfillSerialNumbers()
    old_count = getLatestCount()
    print(old_count)
    new_count = old_count + 1
    print(new_count)
    updateCounter(new_count)
    print(getLatestCount())
    return 0
    
def backfillSerialNumbers():
    all_tasks = []
    try:
        response = table.scan()
        all_tasks = response['Items']
        
        while response.get('LastEvaluatedKey'):
            response = table.scan(
                ExclusiveStartKey=response['LastEvaluatedKey'],
                )
            all_tasks.extend(response['Items'])
            
        for task in all_tasks:
            task['timestamp'] = float(task['timestamp'])
        
        sorted_tasks = sorted(all_tasks, key = lambda task: task['timestamp'],reverse=False)
        counter = 1
        for task in sorted_tasks:
            print(counter)
            print(task['timestamp'])
            response = table.update_item(
                Key={
                    'taskId': task['taskId']
                },
                UpdateExpression="set serialNumber = :serialNumber",
                ExpressionAttributeValues={
                    ':serialNumber': counter
                    },
                ReturnValues="UPDATED_NEW"
            )
            counter += 1
    except:
        raise
    return len(all_tasks)
    
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